# main.py
from flask import Flask, request, jsonify

# Initialize the Flask app
app = Flask(__name__)

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