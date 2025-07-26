#!/usr/bin/env python3
"""
Test script to verify the Slack SDK implementation works correctly.
Run this script to test the basic functionality.
"""

import os
from dotenv import load_dotenv
from tools.slack_tool import (
    slack_post_message,
    slack_fetch_messages,
    slack_get_user_profile,
    slack_get_channel_info
)

def test_slack_sdk():
    """Test the Slack SDK implementation"""
    load_dotenv()
    
    # Check if required environment variables are set
    if not os.getenv("SLACK_BOT_TOKEN"):
        print("❌ SLACK_BOT_TOKEN not set in environment")
        return False
    
    if not os.getenv("SLACK_CHANNEL_ID"):
        print("❌ SLACK_CHANNEL_ID not set in environment")
        return False
    
    channel_id = os.getenv("SLACK_CHANNEL_ID")
    
    print("🧪 Testing Slack SDK implementation...")
    
    try:
        # Test 1: Get channel info
        print("1. Testing channel info...")
        channel_info = slack_get_channel_info(channel_id)
        print(f"   ✅ Channel: {channel_info.get('name', 'Unknown')}")
        print(f"   ✅ Members: {len(channel_info.get('members', []))}")
        
        # Test 2: Fetch messages
        print("2. Testing message fetch...")
        messages = slack_fetch_messages(channel_id, limit=5)
        print(f"   ✅ Fetched {len(messages)} messages")
        
        # Test 3: Get user profile (if there are messages)
        if messages and messages[0].get('user'):
            user_id = messages[0]['user']
            print(f"3. Testing user profile for {user_id}...")
            user_profile = slack_get_user_profile(user_id)
            print(f"   ✅ User: {user_profile.get('real_name', 'Unknown')}")
            print(f"   ✅ Email: {user_profile.get('email', 'No email')}")
        
        # Test 4: Post a test message
        print("4. Testing message posting...")
        test_message = "🧪 Test message from Slack SDK implementation"
        timestamp = slack_post_message(channel_id, test_message)
        print(f"   ✅ Posted message with timestamp: {timestamp}")
        
        print("\n🎉 All tests passed! Slack SDK implementation is working correctly.")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

if __name__ == "__main__":
    test_slack_sdk() 