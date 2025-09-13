#!/usr/bin/env python3
"""
Webhook server for handling Zapier notifications about new NVIDIA blog posts.
This server runs alongside the Streamlit app to process real-time updates.
"""

import os
import sys
import json
import hmac
import hashlib
import logging
from datetime import datetime
from pathlib import Path
from threading import Thread
import asyncio
from typing import Dict, Any, List

from flask import Flask, request, jsonify
from flask_cors import CORS
from waitress import serve
from dotenv import load_dotenv

# Add src directory to path for imports
sys.path.append(str(Path(__file__).parent))

from knowledge_base import KnowledgeBaseProcessor
from web_search_tool import NVIDIABlogSearchTool

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class WebhookServer:
    """Flask server to handle Zapier webhooks for new NVIDIA blog posts."""
    
    def __init__(self):
        """Initialize the webhook server."""
        self.app = Flask(__name__)
        CORS(self.app)  # Enable CORS for cross-origin requests
        
        # Webhook configuration
        self.webhook_secret = os.getenv('WEBHOOK_SECRET', 'nvidia-agent-webhook-secret')
        self.port = int(os.getenv('WEBHOOK_PORT', 5000))
        self.host = os.getenv('WEBHOOK_HOST', '0.0.0.0')
        
        # Initialize components
        self.knowledge_base = None
        self.blog_tool = None
        self._initialize_components()
        
        # Setup routes
        self._setup_routes()
        
        logger.info(f"Webhook server initialized on {self.host}:{self.port}")
    
    def _initialize_components(self):
        """Initialize knowledge base and blog search tool."""
        try:
            self.knowledge_base = KnowledgeBaseProcessor()
            self.blog_tool = NVIDIABlogSearchTool()
            logger.info("Components initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize components: {e}")
    
    def _setup_routes(self):
        """Setup Flask routes for webhooks."""
        
        @self.app.route('/health', methods=['GET'])
        def health_check():
            """Health check endpoint."""
            return jsonify({
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'service': 'nvidia-agent-webhook'
            })
        
        @self.app.route('/webhook/nvidia-blog', methods=['POST'])
        def handle_nvidia_blog_webhook():
            """Handle Zapier webhook for new NVIDIA blog posts."""
            try:
                # Verify webhook authenticity (optional but recommended)
                if not self._verify_webhook_signature(request):
                    logger.warning("Invalid webhook signature")
                    return jsonify({'error': 'Invalid signature'}), 401
                
                # Parse webhook data
                webhook_data = request.get_json()
                if not webhook_data:
                    return jsonify({'error': 'No JSON data received'}), 400
                
                logger.info(f"Received webhook: {webhook_data.get('title', 'Unknown')}")
                
                # Process the new blog post
                result = self._process_new_blog_post(webhook_data)
                
                return jsonify(result)
                
            except Exception as e:
                logger.error(f"Error processing webhook: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/webhook/test', methods=['POST', 'GET'])
        def test_webhook():
            """Test endpoint for webhook development."""
            if request.method == 'POST':
                data = request.get_json() or {}
                logger.info(f"Test webhook received: {data}")
                return jsonify({'status': 'received', 'data': data})
            else:
                return jsonify({
                    'message': 'Webhook test endpoint',
                    'instructions': 'Send POST request with JSON data'
                })
    
    def _verify_webhook_signature(self, request) -> bool:
        """Verify webhook signature for security."""
        # Get signature from header
        signature = request.headers.get('X-Webhook-Signature')
        if not signature:
            return True  # Allow unsigned webhooks for now
        
        # Verify HMAC signature
        expected_signature = hmac.new(
            self.webhook_secret.encode('utf-8'),
            request.get_data(),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(signature, expected_signature)
    
    def _process_new_blog_post(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a new blog post from webhook data."""
        try:
            # Extract data from Zapier webhook
            title = webhook_data.get('title', '')
            url = webhook_data.get('link', '')
            content = webhook_data.get('content', '')
            published_date = webhook_data.get('published', '')
            
            # Validate required fields
            if not title or not url:
                raise ValueError("Missing required fields: title and url")
            
            # Determine source blog
            source = 'NVIDIA Developer Blog' if 'developer.nvidia.com' in url else 'NVIDIA Blog'
            
            # Enhanced content extraction if content is limited
            if len(content) < 200 and self.blog_tool:
                logger.info("Extracting full content from blog URL")
                full_content = self._extract_full_content(url)
                if full_content:
                    content = full_content
            
            # Add to knowledge base
            if self.knowledge_base:
                try:
                    # Use async method in sync context
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    
                    loop.run_until_complete(
                        self.knowledge_base.add_web_content(
                            title=title,
                            content=content,
                            source_url=url,
                            metadata={
                                'source': source,
                                'published_date': published_date,
                                'added_via_webhook': True,
                                'webhook_timestamp': datetime.now().isoformat()
                            }
                        )
                    )
                    
                    loop.close()
                    
                    logger.info(f"Added to knowledge base: {title}")
                    
                except Exception as e:
                    logger.error(f"Failed to add to knowledge base: {e}")
            
            # Save webhook event for Streamlit app to pick up
            self._save_webhook_event({
                'title': title,
                'url': url,
                'source': source,
                'published_date': published_date,
                'processed_at': datetime.now().isoformat(),
                'status': 'success'
            })
            
            return {
                'status': 'success',
                'message': f'Processed blog post: {title}',
                'data': {
                    'title': title,
                    'url': url,
                    'source': source,
                    'content_length': len(content)
                }
            }
            
        except Exception as e:
            logger.error(f"Error processing blog post: {e}")
            
            # Save error event
            self._save_webhook_event({
                'title': webhook_data.get('title', 'Unknown'),
                'url': webhook_data.get('link', 'Unknown'),
                'processed_at': datetime.now().isoformat(),
                'status': 'error',
                'error': str(e)
            })
            
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def _extract_full_content(self, url: str) -> str:
        """Extract full content from blog URL."""
        try:
            if self.blog_tool:
                # Create a mock result object to use the extraction method
                class MockResult:
                    def __init__(self, url):
                        self.url = url
                        self.full_content = None
                
                mock_result = MockResult(url)
                
                # Use async method in sync context
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self.blog_tool._fetch_content(mock_result))
                loop.close()
                
                return mock_result.full_content or ""
            
        except Exception as e:
            logger.error(f"Failed to extract full content: {e}")
            
        return ""
    
    def _save_webhook_event(self, event_data: Dict[str, Any]):
        """Save webhook event for Streamlit app to display."""
        try:
            # Create webhook events directory
            events_dir = Path("data/webhook_events")
            events_dir.mkdir(parents=True, exist_ok=True)
            
            # Save event with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            event_file = events_dir / f"event_{timestamp}.json"
            
            with open(event_file, 'w') as f:
                json.dump(event_data, f, indent=2)
            
            # Keep only recent events (last 50)
            self._cleanup_old_events(events_dir)
            
        except Exception as e:
            logger.error(f"Failed to save webhook event: {e}")
    
    def _cleanup_old_events(self, events_dir: Path, keep_count: int = 50):
        """Clean up old webhook events."""
        try:
            event_files = sorted(events_dir.glob("event_*.json"))
            if len(event_files) > keep_count:
                for old_file in event_files[:-keep_count]:
                    old_file.unlink()
        except Exception as e:
            logger.error(f"Failed to cleanup old events: {e}")
    
    def run(self, debug: bool = False):
        """Run the webhook server."""
        if debug:
            logger.info("Running webhook server in debug mode")
            self.app.run(host=self.host, port=self.port, debug=True)
        else:
            logger.info(f"Running webhook server in production mode on {self.host}:{self.port}")
            serve(self.app, host=self.host, port=self.port)


def main():
    """Main function to run the webhook server."""
    import argparse
    
    parser = argparse.ArgumentParser(description='NVIDIA Agent Webhook Server')
    parser.add_argument('--debug', action='store_true', help='Run in debug mode')
    parser.add_argument('--port', type=int, default=5000, help='Port to run server on')
    parser.add_argument('--host', default='0.0.0.0', help='Host to run server on')
    
    args = parser.parse_args()
    
    # Override environment variables with command line args
    os.environ['WEBHOOK_PORT'] = str(args.port)
    os.environ['WEBHOOK_HOST'] = args.host
    
    # Create and run server
    server = WebhookServer()
    
    try:
        server.run(debug=args.debug)
    except KeyboardInterrupt:
        logger.info("Webhook server stopped by user")
    except Exception as e:
        logger.error(f"Webhook server error: {e}")


if __name__ == "__main__":
    main()
