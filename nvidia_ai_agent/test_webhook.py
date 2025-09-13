#!/usr/bin/env python3
"""
Test script for webhook functionality.
This script simulates Zapier sending webhook notifications.
"""

import requests
import json
from datetime import datetime

def test_webhook_server():
    """Test the webhook server with sample data."""
    
    # Webhook URL
    webhook_url = "http://localhost:5000/webhook/nvidia-blog"
    
    # Sample webhook data (simulating Zapier)
    test_data = {
        "title": "New NVIDIA AI Breakthrough: Advanced RAG Systems",
        "link": "https://developer.nvidia.com/blog/new-ai-breakthrough-rag-systems",
        "content": "This is a sample blog post about NVIDIA's latest advances in Retrieval Augmented Generation systems. The post covers new techniques for improving accuracy and performance in AI applications.",
        "published": datetime.now().isoformat(),
        "description": "Learn about NVIDIA's newest AI innovations in RAG technology"
    }
    
    print("🧪 Testing webhook server...")
    print(f"📡 Webhook URL: {webhook_url}")
    print(f"📄 Test data: {test_data['title']}")
    
    try:
        # Send test webhook
        response = requests.post(
            webhook_url,
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"📊 Response Status: {response.status_code}")
        print(f"📋 Response Data: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ Webhook test successful!")
            return True
        else:
            print("❌ Webhook test failed!")
            return False
            
    except requests.ConnectionError:
        print("❌ Cannot connect to webhook server. Is it running?")
        print("   Start it with: python src/webhook_server.py")
        return False
    except Exception as e:
        print(f"❌ Webhook test error: {e}")
        return False


def test_health_check():
    """Test the health check endpoint."""
    
    health_url = "http://localhost:5000/health"
    
    print("\n🏥 Testing health check endpoint...")
    
    try:
        response = requests.get(health_url, timeout=5)
        print(f"📊 Health Status: {response.status_code}")
        print(f"📋 Health Data: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ Health check successful!")
            return True
        else:
            print("❌ Health check failed!")
            return False
            
    except requests.ConnectionError:
        print("❌ Cannot connect to webhook server")
        return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False


def main():
    """Run webhook tests."""
    
    print("🔬 NVIDIA Agent Webhook Test Suite")
    print("=" * 50)
    
    # Test health check first
    health_ok = test_health_check()
    
    if health_ok:
        # Test webhook functionality
        webhook_ok = test_webhook_server()
        
        if webhook_ok:
            print("\n🎉 All tests passed!")
            print("💡 Check the Streamlit app for webhook notifications")
            print("📁 Check data/webhook_events/ for saved events")
        else:
            print("\n❌ Webhook tests failed")
    else:
        print("\n❌ Server not available")
        print("💡 Start the webhook server first:")
        print("   python src/webhook_server.py")


if __name__ == "__main__":
    main()
