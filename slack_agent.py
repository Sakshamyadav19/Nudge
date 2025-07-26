# slack_tool.py
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

class SlackTool:
    def __init__(self, token: str):
        self.client = WebClient(token=token)

    # grab last N msgs when the server starts
    def last_messages(self, channel, limit=50):
        resp = self.client.conversations_history(channel=channel,
                                                 limit=limit)        # :contentReference[oaicite:0]{index=0}
        return resp["messages"]

    # post updates back to the same channel
    def post(self, channel, text, thread_ts=None):
        self.client.chat_postMessage(channel=channel,
                                     text=text,
                                     thread_ts=thread_ts)
    
    # look-up Slack → Jira assignee mapping
    def user_profile(self, user_id):
        return self.client.users_info(user=user_id)["user"]
