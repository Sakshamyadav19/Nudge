# mcp_agent.py
import os
import requests
from llama_index.agent import AgentGraph, ToolNode, SimpleRouter
from llama_index.llms import OpenAI
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
        
        return f"Ticket {key} created"
    except Exception as e:
        return f"Error creating ticket: {str(e)}"

# ─────────────── ROUTING LOGIC ───────────────
def classify_action(query: str) -> str:
    """
    Enhanced router that considers conversation context for better decision making.
    """
    # Get conversation context to inform the decision
    context = get_conversation_context()
    
    query_lower = query.lower()
    
    # Enhanced keyword detection with context awareness
    if any(keyword in query_lower for keyword in ["assign", "please", "task", "ticket", "issue", "bug"]):
        return "jira"
    elif any(keyword in query_lower for keyword in ["meeting", "schedule", "calendar", "event"]):
        return "calendar"
    else:
        return "noop"

router = SimpleRouter(decide_fn=lambda q: classify_action(q["text"]))

# ─────────────── TOOL NODES ───────────────
nodes = {
    "jira": ToolNode(func=lambda q: create_jira_ticket(q["text"], q["slack_user"])),
    "calendar": ToolNode(func=lambda q: "Calendar functionality coming soon"),
    "noop": ToolNode(func=lambda q: "No action needed")
}

# ─────────────── BUILD AGENT GRAPH ───────────────
graph = AgentGraph(nodes=nodes, router=router)
mcp_agent = graph.as_agent(llm=llm)

# ─────────────── ENHANCED PROCESSING FUNCTION ───────────────
def process_message_with_context(text: str, slack_user: str):
    """
    Process a message with conversation context for better understanding.
    """
    try:
        # Get conversation context
        context = get_conversation_context()
        
        # Create enhanced query with context
        enhanced_query = f"""
Conversation Context:
{context}

Current Message: {text}
User: {slack_user}

Please analyze this message in the context of the conversation above and determine the appropriate action.
"""
        
        # Process with the agent
        result = mcp_agent.query(enhanced_query)
        
        # Also try direct classification for immediate action
        action = classify_action(text)
        
        if action == "jira":
            # Create Jira ticket directly
            ticket_result = create_jira_ticket(text, slack_user)
            return f"Action: {action}, Result: {ticket_result}"
        elif action == "calendar":
            return f"Action: {action}, Result: Calendar functionality coming soon"
        else:
            return f"Action: {action}, Result: No action needed"
            
    except Exception as e:
        print(f"Error in process_message_with_context: {e}")
        return f"Error processing message: {str(e)}"
