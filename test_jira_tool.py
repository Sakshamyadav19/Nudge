#!/usr/bin/env python3
"""
Test script to verify the Jira tool works correctly with the new REST API implementation.
"""

import os
from dotenv import load_dotenv
from tools.jira_tool import jira_create_issue

def test_jira_tool():
    """Test the Jira tool functionality"""
    load_dotenv()
    
    # Check if required environment variables are set
    required_vars = ["JIRA_BASE_URL", "JIRA_EMAIL", "JIRA_API_TOKEN"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Please set these in your .env file:")
        for var in missing_vars:
            print(f"  {var}=your-value-here")
        return False
    
    print("🧪 Testing Jira tool...")
    
    try:
        # Test creating a simple issue
        test_title = "Test issue from Slack bot"
        test_summary = "This is a test issue created by the Slack bot"
        test_description = "This issue was created to test the Jira tool integration."
        
        print(f"Creating test issue with title: '{test_title}'")
        
        issue_key = jira_create_issue(
            title=test_title,
            project_key="PROJ",  # Change this to your actual project key
            summary=test_summary,
            description=test_description,
            issue_type="Task"
        )
        
        print(f"✅ Successfully created Jira issue: {issue_key}")
        print(f"🔗 View at: {os.getenv('JIRA_BASE_URL')}/browse/{issue_key}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

if __name__ == "__main__":
    test_jira_tool() 