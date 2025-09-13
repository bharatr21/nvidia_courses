"""
Cloud-compatible webhook handler for Streamlit Cloud deployment.
Since Streamlit Cloud doesn't support separate webhook servers, this uses external services.
"""

import os
import json
import requests
from datetime import datetime
from typing import Dict, Any, List
import streamlit as st
from pathlib import Path

class CloudWebhookHandler:
    """Handle webhooks in Streamlit Cloud environment using external services."""
    
    def __init__(self):
        """Initialize cloud webhook handler."""
        self.is_cloud = os.getenv('STREAMLIT_CLOUD', 'false').lower() == 'true'
        self.webhook_service_url = os.getenv('EXTERNAL_WEBHOOK_URL', '')
        self.webhook_secret = os.getenv('WEBHOOK_SECRET', 'default-secret')
        
    def check_external_webhook_events(self) -> List[Dict[str, Any]]:
        """Check for new events from external webhook service."""
        if not self.webhook_service_url:
            return []
            
        try:
            # Call external webhook service API to get recent events
            response = requests.get(
                f"{self.webhook_service_url}/events/recent",
                headers={'Authorization': f'Bearer {self.webhook_secret}'},
                timeout=10
            )
            
            if response.status_code == 200:
                events = response.json().get('events', [])
                return events
            
        except Exception:
            pass  # Silently fail for cloud deployment
            
        return []
    
    def simulate_webhook_for_testing(self) -> List[Dict[str, Any]]:
        """Simulate webhook events for testing purposes."""
        # This creates fake events for demonstration
        fake_events = [
            {
                'title': 'NVIDIA Announces New AI Microservices',
                'url': 'https://developer.nvidia.com/blog/new-ai-microservices',
                'source': 'NVIDIA Developer Blog', 
                'published_date': '2024-01-15',
                'processed_at': datetime.now().isoformat(),
                'status': 'success',
                'content_summary': 'Latest developments in NVIDIA NIM architecture...'
            }
        ]
        return fake_events
    
    def get_webhook_events(self) -> List[Dict[str, Any]]:
        """Get webhook events based on deployment environment."""
        if self.is_cloud:
            # In cloud, try external service or return empty
            return self.check_external_webhook_events()
        else:
            # Local deployment - check local webhook files
            return self._check_local_webhook_files()
    
    def _check_local_webhook_files(self) -> List[Dict[str, Any]]:
        """Check local webhook event files."""
        try:
            events_dir = Path("data/webhook_events")
            if not events_dir.exists():
                return []
            
            events = []
            event_files = sorted(events_dir.glob("event_*.json"))[-10:]  # Last 10 events
            
            for event_file in event_files:
                try:
                    with open(event_file, 'r') as f:
                        event_data = json.load(f)
                        events.append(event_data)
                except Exception:
                    continue
                    
            return events
            
        except Exception:
            return []
    
    def display_cloud_webhook_setup(self):
        """Display webhook setup instructions for cloud deployment."""
        if not self.is_cloud:
            return
            
        st.sidebar.info("🌐 **Streamlit Cloud Deployment**")
        
        if not self.webhook_service_url:
            with st.sidebar.expander("📡 Webhook Setup Required"):
                st.markdown("""
                **For real-time updates, set up external webhook service:**
                
                1. **Option 1: Use Zapier + Google Sheets**
                   - RSS Feed → Google Sheets → Streamlit reads sheets
                
                2. **Option 2: Use Zapier + GitHub**
                   - RSS Feed → GitHub file update → Streamlit reads file
                
                3. **Option 3: External API Service**
                   - Deploy simple webhook API (Vercel/Netlify)
                   - Set `EXTERNAL_WEBHOOK_URL` in secrets
                
                **Current Status:** No external webhook configured
                """)
        else:
            st.sidebar.success("🔗 External webhook service configured")


def setup_cloud_webhooks_with_github():
    """Instructions for GitHub-based webhook setup."""
    instructions = """
    # 🚀 GitHub-Based Webhook Setup for Streamlit Cloud
    
    Since Streamlit Cloud can't run webhook servers, use this GitHub approach:
    
    ## Step 1: Create GitHub Action for RSS Monitoring
    
    ```yaml
    # .github/workflows/nvidia-blog-monitor.yml
    name: NVIDIA Blog Monitor
    on:
      schedule:
        - cron: '0 12 * * *'  # Daily at noon
      workflow_dispatch:
    
    jobs:
      check-blogs:
        runs-on: ubuntu-latest
        steps:
          - uses: actions/checkout@v3
          - name: Check RSS feeds
            run: |
              python scripts/check_nvidia_blogs.py
          - name: Commit new posts
            run: |
              git config --local user.email "action@github.com"
              git config --local user.name "GitHub Action"
              git add data/webhook_events/
              git commit -m "Add new blog posts" || exit 0
              git push
    ```
    
    ## Step 2: Zapier Alternative Setup
    
    1. **Zapier Zap Configuration:**
       - Trigger: RSS by Zapier (NVIDIA feeds)
       - Action: GitHub - Create/Update File
       - File path: `data/webhook_events/event_{{timestamp}}.json`
    
    2. **JSON Format:**
    ```json
    {
      "title": "{{title}}",
      "url": "{{link}}", 
      "content": "{{content}}",
      "published": "{{published}}",
      "source": "NVIDIA Developer Blog",
      "processed_at": "{{timestamp}}",
      "status": "success"
    }
    ```
    
    ## Step 3: Streamlit Cloud Configuration
    
    Add to your Streamlit secrets:
    ```
    STREAMLIT_CLOUD = "true"
    GITHUB_WEBHOOK_MODE = "true"
    ```
    """
    
    return instructions


# Initialize cloud webhook handler
cloud_webhook_handler = CloudWebhookHandler()
