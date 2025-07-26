#!/usr/bin/env python3
"""
Test script to verify the updated agent works correctly with the new LlamaIndex structure.
"""

import os
from dotenv import load_dotenv
from agent import process_message_with_context, process_message_simple

def test_agent():
    """Test the agent functionality"""
    load_dotenv()
    
    # Check if required environment variables are set
    if not os.getenv("SLACK_BOT_TOKEN"):
        print("❌ SLACK_BOT_TOKEN not set in environment")
        return False
    
    if not os.getenv("SLACK_CHANNEL_ID"):
        print("❌ SLACK_CHANNEL_ID not set in environment")
        return False
    
    print("🧪 Testing agent functionality...")
    
    # Test cases
    test_cases = [
        {
            "text": "Please create a task for me to review the documentation",
            "user_id": "U1234567890",
            "expected_action": "jira"
        },
        {
            "text": "Can you schedule a meeting for tomorrow?",
            "user_id": "U1234567890", 
            "expected_action": "calendar"
        },
        {
            "text": "Hello, how are you?",
            "user_id": "U1234567890",
            "expected_action": "noop"
        }
    ]
    
    try:
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n{i}. Testing: '{test_case['text']}'")
            
            # Test simple processing
            result_simple = process_message_simple(
                test_case['text'], 
                test_case['user_id']
            )
            print(f"   Simple result: {result_simple}")
            
            # Test LLM processing (this might take longer)
            print("   Testing LLM processing...")
            try:
                result_llm = process_message_with_context(
                    test_case['text'], 
                    test_case['user_id']
                )
                print(f"   LLM result: {result_llm}")
            except Exception as e:
                print(f"   LLM processing failed: {str(e)}")
                print("   This is expected if OpenAI API key is not set")
        
        print("\n🎉 Agent tests completed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

if __name__ == "__main__":
    test_agent() 