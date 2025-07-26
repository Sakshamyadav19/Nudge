# main.py
from flask import Flask, request, jsonify
import os
import json
from datetime import datetime
from dotenv import load_dotenv
from tools.slack_tool import slack_fetch_messages, slack_post_message, slack_get_user_profile, slack_get_channel_info

load_dotenv()

# Initialize the Flask app
app = Flask(__name__)

# Global variable to store conversation context
conversation_context = {
    "messages": [],
    "last_updated": None,
    "channel_id": None
}

def fetch_conversation_context(channel_id=None):
    """Fetch the last 50 messages and store as conversation context"""
    global conversation_context
    
    # Use default channel if none provided
    if not channel_id:
        channel_id = os.getenv("SLACK_CHANNEL_ID")
    
    if not channel_id:
        print("⚠️  No channel_id provided and SLACK_CHANNEL_ID not set in environment")
        return
    
    try:
        print(f"🔄 Fetching last 50 messages from channel {channel_id}...")
        
        messages = slack_fetch_messages(channel_id=channel_id, limit=50)
        
        # Update conversation context
        conversation_context = {
            "messages": messages,
            "last_updated": datetime.now().isoformat(),
            "channel_id": channel_id
        }
        
        print(f"✅ Successfully fetched {len(messages)} messages")
        print(f"📝 Conversation context updated at {conversation_context['last_updated']}")
        
        # Save context to file for persistence
        save_context_to_file()
        
    except RuntimeError as e:
        print(f"❌ Error fetching conversation context: {e}")
    except Exception as e:
        print(f"❌ Unexpected error fetching conversation context: {e}")

def save_context_to_file():
    """Save conversation context to a JSON file"""
    try:
        with open("conversation_context.json", "w") as f:
            json.dump(conversation_context, f, indent=2)
        print("💾 Conversation context saved to file")
    except Exception as e:
        print(f"❌ Error saving context to file: {e}")

def load_context_from_file():
    """Load conversation context from JSON file"""
    global conversation_context
    try:
        if os.path.exists("conversation_context.json"):
            with open("conversation_context.json", "r") as f:
                conversation_context = json.load(f)
            print(f"📂 Loaded conversation context from file ({len(conversation_context.get('messages', []))} messages)")
        else:
            print("📂 No existing conversation context file found")
    except Exception as e:
        print(f"❌ Error loading context from file: {e}")

def get_conversation_context_for_llm():
    """Format conversation context for LLM consumption"""
    if not conversation_context.get("messages"):
        return "No conversation history available."
    
    context_lines = []
    context_lines.append(f"Conversation context from Slack channel {conversation_context['channel_id']}:")
    context_lines.append(f"Last updated: {conversation_context['last_updated']}")
    context_lines.append("Recent messages (newest first):")
    context_lines.append("-" * 50)
    
    # Format messages for LLM consumption
    for msg in conversation_context["messages"][:20]:  # Limit to last 20 for context
        user = msg.get("user", "Unknown")
        text = msg.get("text", "")
        ts = msg.get("ts", "")
        
        # Convert timestamp to readable format
        try:
            dt = datetime.fromtimestamp(float(ts))
            time_str = dt.strftime("%Y-%m-%d %H:%M:%S")
        except:
            time_str = ts
        
        context_lines.append(f"[{time_str}] {user}: {text}")
    
    return "\n".join(context_lines)

# ——— Arcade Slack Endpoints ———

@app.route("/api/arcade/slack/messages", methods=["GET"])
def get_slack_messages():
    """Get the last 50 messages from a Slack channel"""
    try:
        channel_id = request.args.get("channel_id")
        limit = int(request.args.get("limit", 50))
        
        if not channel_id:
            return jsonify({"error": "channel_id is required"}), 400
        
        messages = slack_fetch_messages(channel_id=channel_id, limit=limit)
        return jsonify({"messages": messages, "count": len(messages)})
        
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500

@app.route("/api/arcade/slack/user-profile", methods=["GET"])
def get_user_profile():
    """Get a Slack user's profile"""
    try:
        user_id = request.args.get("user_id")
        
        if not user_id:
            return jsonify({"error": "user_id is required"}), 400
        
        user_profile = slack_get_user_profile(user_id=user_id)
        return jsonify(user_profile)
        
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500

@app.route("/api/arcade/slack/send-message", methods=["POST"])
def send_slack_message():
    """Send a message to a Slack channel"""
    try:
        data = request.json
        
        if not data:
            return jsonify({"error": "Request body is required"}), 400
        
        channel_id = data.get("channel_id")
        text = data.get("text")
        thread_ts = data.get("thread_ts")
        
        if not channel_id or not text:
            return jsonify({"error": "channel_id and text are required"}), 400
        
        payload = {
            "channel_id": channel_id,
            "text": text
        }
        
        if thread_ts:
            payload["thread_ts"] = thread_ts

        timestamp = slack_post_message(channel_id=channel_id, text=text, thread_ts=thread_ts)
        return jsonify({"success": True, "timestamp": timestamp})
        
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500

@app.route("/api/arcade/slack/channel-users", methods=["GET"])
def get_channel_users():
    """Get user profiles for all users in a channel"""
    try:
        channel_id = request.args.get("channel_id")
        
        if not channel_id:
            return jsonify({"error": "channel_id is required"}), 400
        
        # First get channel info to get member list
        channel_info = slack_get_channel_info(channel_id=channel_id)
        members = channel_info.get("members", [])
        
        # Get profiles for each member
        user_profiles = []
        for user_id in members:
            try:
                user_profile = slack_get_user_profile(user_id=user_id)
                user_profiles.append(user_profile)
            except Exception as e:
                print(f"Failed to get profile for user {user_id}: {e}")
                continue
        
        return jsonify({"users": user_profiles, "count": len(user_profiles)})
        
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500

# ——— Conversation Context Endpoints ———

@app.route("/api/conversation/context", methods=["GET"])
def get_conversation_context():
    """Get the current conversation context for LLM"""
    try:
        context_text = get_conversation_context_for_llm()
        return jsonify({
            "context": context_text,
            "metadata": {
                "message_count": len(conversation_context.get("messages", [])),
                "last_updated": conversation_context.get("last_updated"),
                "channel_id": conversation_context.get("channel_id")
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/conversation/refresh", methods=["POST"])
def refresh_conversation_context():
    """Manually refresh the conversation context"""
    try:
        channel_id = request.json.get("channel_id") if request.json else None
        fetch_conversation_context(channel_id)
        return jsonify({
            "success": True,
            "message": f"Conversation context refreshed with {len(conversation_context.get('messages', []))} messages"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/test/agent", methods=["POST"])
def test_agent():
    """Test the MCP agent with a sample message"""
    try:
        data = request.json or {}
        text = data.get("text", "Please create a task for me")
        user_id = data.get("user_id", "U1234567890")
        
        from agent import process_message_with_context
        
        result = process_message_with_context(text, user_id)
        
        return jsonify({
            "success": True,
            "input": {"text": text, "user_id": user_id},
            "result": result
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ——— Original Slack Events Endpoint ———

# This is the endpoint Slack will send messages to
@app.route("/api/slack/events", methods=["POST"])
def slack_events():
    data = request.json

    # Slack's URL verification challenge
    if "challenge" in data:
        return jsonify({"challenge": data["challenge"]})

    # Process Slack events
    print("Received event from Slack:")
    print(data)

    # Check if this is a message event
    if data.get("event", {}).get("type") == "message":
        event = data["event"]
        
        # Skip bot messages and message edits/deletions
        if event.get("bot_id") or event.get("subtype") in ["message_changed", "message_deleted"]:
            print("Skipping bot message or message edit/deletion")
            return jsonify({"status": "ok"}), 200
        
        # Extract message details
        text = event.get("text", "")
        user_id = event.get("user", "")
        channel_id = event.get("channel", "")
        ts = event.get("ts", "")
        
        # Skip empty messages
        if not text.strip():
            print("Skipping empty message")
            return jsonify({"status": "ok"}), 200
        
        print(f"🤖 Processing message: '{text}' from user {user_id} in channel {channel_id}")
        
        # Process message through MCP agent
        try:
            from agent import process_message_with_context
            
            # Refresh conversation context to include the latest messages
            print("🔄 Refreshing conversation context...")
            fetch_conversation_context(channel_id)
            
            # Process the message with conversation context
            result = process_message_with_context(text, user_id)
            
            print(f"Agent result: {result}")
            
            # If the agent created a Jira ticket, the confirmation message will be sent automatically
            # by the agent's create_jira_ticket function
            
        except Exception as e:
            print(f"Error processing message through agent: {e}")
            # Don't fail the webhook - just log the error
    
    # We need to respond to Slack quickly
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    print("🚀 Starting Nudge server...")
    
    # Load existing context from file if available
    load_context_from_file()
    
    # Fetch fresh conversation context on startup
    print("📥 Fetching conversation context on startup...")
    fetch_conversation_context()
    
    # Print startup summary
    print(f"📊 Server ready with {len(conversation_context.get('messages', []))} messages in context")
    print(f"🌐 Server will run on port 3000")
    print("=" * 50)
    
    # Run the server on port 3000
    app.run(port=3000, debug=True)