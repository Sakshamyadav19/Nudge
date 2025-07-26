#!/usr/bin/env python3
"""
Debug script to see the actual structure of Arcade response.
"""

import os
from dotenv import load_dotenv
from arcadepy import Arcade

def debug_arcade_response():
    """Debug the Arcade response structure"""
    load_dotenv()
    
    if not os.getenv("ARCADE_API_KEY") or not os.getenv("ARCADE_USER_ID"):
        print("❌ ARCADE_API_KEY and ARCADE_USER_ID required")
        return
    
    try:
        client = Arcade(api_key=os.getenv("ARCADE_API_KEY"))
        
        # Test the response structure
        res = client.tools.execute(
            tool_name="Jira.CreateIssue",
            input={
                "title": "Debug test issue",
                "project_key": "TEST",
                "summary": "Debug test",
                "description": "This is a debug test",
                "issue_type": "Task"
            },
            user_id=os.getenv("ARCADE_USER_ID")
        )
        
        print("🔍 Debugging Arcade response structure:")
        print(f"Success: {res.success}")
        print(f"Type of res: {type(res)}")
        print(f"Dir of res: {dir(res)}")
        
        if hasattr(res, 'output'):
            print(f"Type of res.output: {type(res.output)}")
            print(f"Dir of res.output: {dir(res.output)}")
            print(f"res.output: {res.output}")
            
            if hasattr(res.output, 'get'):
                print("res.output has .get() method")
                print(f"res.output.get('created_key'): {res.output.get('created_key')}")
                print(f"res.output.get('key'): {res.output.get('key')}")
            else:
                print("res.output does NOT have .get() method")
                
            if hasattr(res.output, 'created_key'):
                print(f"res.output.created_key: {res.output.created_key}")
            if hasattr(res.output, 'key'):
                print(f"res.output.key: {res.output.key}")
        else:
            print("res has no 'output' attribute")
            
        print(f"String representation: {str(res)}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_arcade_response() 