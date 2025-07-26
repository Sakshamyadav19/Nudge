# mcp_agent.py
import os
import requests
from llama_index.llms.openai import OpenAI
from tools.slack_tool import slack_post_message, slack_get_user_profile
from tools.jira_tool import jira_create_issue

# ─────────────── INIT TOOLS ───────────────
llm = OpenAI(model="gpt-4o")

def get_conversation_context():
    """Get conversation context from the main server"""
    try:
        response = requests.get("http://localhost:3000/api/conversation/context")
        if response.status_code == 200:
            return response.json().get("context", "No conversation context available.")
        else:
            return "Failed to fetch conversation context."
    except Exception as e:
        return f"Error fetching conversation context: {str(e)}"

# ─────────────── WRAPPER FUNCTION ───────────────
def create_jira_ticket(text, slack_user):
    """Create a Jira ticket for the given task"""
    try:
        # Get user profile using the new tool
        profile = slack_get_user_profile(user_id=slack_user)
        email = profile.get("email", "unknown@example.com")
        
        # Create Jira ticket using the new tool
        key = jira_create_issue(
            title=text[:120],
            project_key="PROJ",
            summary=text[:120],
            description=f"Raised from Slack:\n\n{text}",
            issue_type="Task"
        )
        
        # Post confirmation message using the new tool
        slack_post_message(
            channel_id=os.environ["SLACK_CHANNEL_ID"],
            text=f"🎫 Created Jira ticket `{key}` for task: {text}"
        )
        
        return f"Ticket {key} created successfully"
    except Exception as e:
        return f"Error creating ticket: {str(e)}"

def schedule_calendar_event(text, slack_user):
    """Schedule a calendar event (placeholder for future implementation)"""
    return "Calendar functionality coming soon"

# ─────────────── SIMPLE CLASSIFICATION FUNCTION ───────────────
def classify_action(query: str) -> str:
    """
    Simple router that classifies the action needed based on keywords.
    """
    query_lower = query.lower()
    
    # Keyword detection
    if any(keyword in query_lower for keyword in ["assign", "please", "task", "ticket", "issue", "bug", "create"]):
        return "jira"
    elif any(keyword in query_lower for keyword in ["meeting", "schedule", "calendar", "event"]):
        return "calendar"
    else:
        return "noop"

# ─────────────── ENHANCED PROCESSING FUNCTION ───────────────
def process_message_with_context(text: str, slack_user: str):
    """
    Process a message with conversation context for better understanding.
    """
    try:
        # Get conversation context
        context = get_conversation_context()
        
        # Use simple classification for now
        action = classify_action(text)
        
        if action == "jira":
            result = create_jira_ticket(text, slack_user)
            return f"Action: {action}, Result: {result}"
        elif action == "calendar":
            result = schedule_calendar_event(text, slack_user)
            return f"Action: {action}, Result: {result}"
        else:
            return f"Action: {action}, Result: No action needed"
            
    except Exception as e:
        print(f"Error in process_message_with_context: {e}")
        return f"Error processing message: {str(e)}"

def process_message_simple(text: str, slack_user: str):
    """
    Simple message processing without LLM agent (fallback).
    """
    try:
        action = classify_action(text)
        
        if action == "jira":
            result = create_jira_ticket(text, slack_user)
            return f"Action: {action}, Result: {result}"
        elif action == "calendar":
            result = schedule_calendar_event(text, slack_user)
            return f"Action: {action}, Result: {result}"
        else:
            return f"Action: {action}, Result: No action needed"
            
    except Exception as e:
        print(f"Error in process_message_simple: {e}")
        return f"Error processing message: {str(e)}"
