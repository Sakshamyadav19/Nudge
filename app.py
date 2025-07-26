# app.py

import os, hmac, hashlib, json
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

SLACK_SIGNING_SECRET = os.environ["SLACK_SIGNING_SECRET"]
SLACK_BOT_TOKEN       = os.environ["SLACK_BOT_TOKEN"]

def verify_slack(req):
    timestamp = req.headers.get("X-Slack-Request-Timestamp", "")
    sig_basestring = f"v0:{timestamp}:{req.get_data(as_text=True)}"
    my_sig = "v0=" + hmac.new(
        SLACK_SIGNING_SECRET.encode(),
        sig_basestring.encode(),
        hashlib.sha256
    ).hexdigest()
    slack_sig = req.headers.get("X-Slack-Signature", "")
    return hmac.compare_digest(my_sig, slack_sig)

def post_confirmation(channel, text):
    url = "https://slack.com/api/chat.postMessage"
    headers = {"Authorization": f"Bearer {SLACK_BOT_TOKEN}"}
    data = {"channel": channel, "text": text}
    requests.post(url, headers=headers, json=data)

@app.route("/slack/events", methods=["POST"])
def slack_events():
    # 1. Verify request
    if not verify_slack(request):
        return "Invalid signature", 403

    payload = request.get_json()
    # 2. URL Verification challenge
    if payload.get("type") == "url_verification":
        return jsonify({"challenge": payload["challenge"]})

    # 3. Handle incoming events
    if payload.get("type") == "event_callback":
        ev = payload["event"]
        # Ignore bot messages
        if ev.get("subtype") == "bot_message":
            return "", 200

        user    = ev.get("user")
        channel = ev.get("channel")
        text    = ev.get("text")

        # 4. Send to ClerkAI pipeline: parse & handle
        action_json = call_llm_parse(text)         # your function
        handle_action(action_json)                 # your pipeline

        # 5. (Optional) confirm back in Slack
        post_confirmation(channel, "✅ Done—your request was handled!")

    return "", 200


if __name__ == "__main__":
    app.run(port=3000)
