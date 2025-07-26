#!/usr/bin/env python3
"""
Test script to verify if Arcade Jira integration is working correctly.
"""

import os
from dotenv import load_dotenv

def test_arcade_setup():
    """Test Arcade setup and authorization"""
    load_dotenv()
    
    # Check if required environment variables are set
    if not os.getenv("ARCADE_API_KEY"):
        print("❌ ARCADE_API_KEY not set in environment")
        return False
    
    if not os.getenv("ARCADE_USER_ID"):
        print("❌ ARCADE_USER_ID not set in environment")
        return False
    
    print("🧪 Testing Arcade setup...")
    
    try:
        # Test importing Arcade
        print("1. Testing Arcade import...")
        from arcadepy import Arcade
        print("   ✅ Arcade import successful")
        
        # Test client initialization
        print("2. Testing Arcade client initialization...")
        client = Arcade(api_key=os.getenv("ARCADE_API_KEY"))
        print("   ✅ Arcade client initialized")
        
        # Test authorization
        print("3. Testing Jira tool authorization...")
        auth = client.tools.authorize(
            tool_name="Jira.CreateIssue",
            user_id=os.getenv("ARCADE_USER_ID")
        )
        
        if auth.status == "completed":
            print("   ✅ Jira tool already authorized")
        elif auth.status == "pending":
            print("   ⏳ Authorization pending - visit this URL:")
            print(f"   {auth.url}")
            print("   After authorization, run this test again")
            return False
        else:
            print(f"   ❌ Authorization failed with status: {auth.status}")
            return False
        
        # Test tool execution (dry run)
        print("4. Testing tool execution...")
        res = client.tools.execute(
            tool_name="Jira.CreateIssue",
            input={
                "title": "Test issue",
                "project_key": "TEST",
                "summary": "Test summary",
                "description": "Test description",
                "issue_type": "Task"
            },
            user_id=os.getenv("ARCADE_USER_ID")
        )
        
        if res.success:
            print("   ✅ Tool execution successful")
            print(f"   Response: {res.output}")
        else:
            print(f"   ❌ Tool execution failed: {res.error_message}")
            return False
        
        print("\n🎉 Arcade Jira integration is working correctly!")
        return True
        
    except ImportError as e:
        print(f"❌ Failed to import Arcade: {e}")
        print("   Make sure arcadepy is installed: pip install arcadepy")
        return False
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

if __name__ == "__main__":
    test_arcade_setup() 