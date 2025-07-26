# main.py
from flask import Flask, request, jsonify
import os
from arcadepy import Arcade

# Initialize the Flask app
app = Flask(__name__)

# Initialize Arcade client
client = Arcade(api_key=os.getenv("ARCADE_API_KEY"))
USER_ID = os.getenv("ARCADE_USER_ID")

# ——— Arcade Slack Endpoints ———

@app.route("/api/arcade/slack/messages", methods=["GET"])
def get_slack_messages():
    """Get the last 50 messages from a Slack channel"""
    try:
        channel_id = request.args.get("channel_id")
        limit = int(request.args.get("limit", 50))
        
        if not channel_id:
            return jsonify({"error": "channel_id is required"}), 400
        
        res = client.tools.execute(
            tool_name="Slack.FetchMessages@2.0.0",
            input={
                "channel_id": channel_id,
                "limit": limit
            },
            user_id=USER_ID,
        )

        if not res.success:
            code = getattr(res, "error_code", None)
            msg = getattr(res, "error_message", str(res))
            return jsonify({"error": f"Arcade tool call failed [{code}]: {msg}"}), 500

        api_error = res.output.get("error")
        if api_error:
            return jsonify({"error": f"Slack API error: {api_error}"}), 500

        messages = res.output.get("messages", [])
        return jsonify({"messages": messages, "count": len(messages)})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/arcade/slack/user-profile", methods=["GET"])
def get_user_profile():
    """Get a Slack user's profile"""
    try:
        user_id = request.args.get("user_id")
        
        if not user_id:
            return jsonify({"error": "user_id is required"}), 400
        
        res = client.tools.execute(
            tool_name="Slack.GetUserProfile@2.0.0",
            input={
                "user_id": user_id
            },
            user_id=USER_ID,
        )

        if not res.success:
            code = getattr(res, "error_code", None)
            msg = getattr(res, "error_message", str(res))
            return jsonify({"error": f"Arcade tool call failed [{code}]: {msg}"}), 500

        api_error = res.output.get("error")
        if api_error:
            return jsonify({"error": f"Slack API error: {api_error}"}), 500

        return jsonify(res.output)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

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

        res = client.tools.execute(
            tool_name="Slack.PostMessage@2.0.0",
            input=payload,
            user_id=USER_ID,
        )

        if not res.success:
            code = getattr(res, "error_code", None)
            msg = getattr(res, "error_message", str(res))
            return jsonify({"error": f"Arcade tool call failed [{code}]: {msg}"}), 500

        api_error = res.output.get("error")
        if api_error:
            return jsonify({"error": f"Slack API error: {api_error}"}), 500

        timestamp = res.output.get("ts", "")
        return jsonify({"success": True, "timestamp": timestamp})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/arcade/slack/channel-users", methods=["GET"])
def get_channel_users():
    """Get user profiles for all users in a channel"""
    try:
        channel_id = request.args.get("channel_id")
        
        if not channel_id:
            return jsonify({"error": "channel_id is required"}), 400
        
        # First get channel info to get member list
        res = client.tools.execute(
            tool_name="Slack.GetChannelInfo@2.0.0",
            input={
                "channel_id": channel_id
            },
            user_id=USER_ID,
        )

        if not res.success:
            code = getattr(res, "error_code", None)
            msg = getattr(res, "error_message", str(res))
            return jsonify({"error": f"Arcade tool call failed [{code}]: {msg}"}), 500

        api_error = res.output.get("error")
        if api_error:
            return jsonify({"error": f"Slack API error: {api_error}"}), 500

        channel_info = res.output
        members = channel_info.get("members", [])
        
        # Get profiles for each member
        user_profiles = []
        for user_id in members:
            try:
                profile_res = client.tools.execute(
                    tool_name="Slack.GetUserProfile@2.0.0",
                    input={"user_id": user_id},
                    user_id=USER_ID,
                )
                
                if profile_res.success and not profile_res.output.get("error"):
                    user_profiles.append(profile_res.output)
            except Exception as e:
                print(f"Failed to get profile for user {user_id}: {e}")
                continue
        
        return jsonify({"users": user_profiles, "count": len(user_profiles)})
        
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

    # For now, just print the whole event to see what we get
    print("Received event from Slack:")
    print(data)

    # We need to respond to Slack quickly
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    # Run the server on port 3000
    app.run(port=3000, debug=True)