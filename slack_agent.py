# slack_tools.py
from typing import Annotated, Optional, List
from arcade_tdk import ToolContext, tool
from arcade_tdk.auth import Slack
from arcade_tdk.errors import RetryableToolError
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


# --- Post a message -------------------------------------------------
@tool(
    name="Slack.PostMessage",
    description="Post a message to a Slack channel (or thread).",
    requires_auth=Slack(scopes=[
        "chat:write",          # needed for chat.postMessage
        "channels:history",    # if you also read from public channels
        "groups:history",      # private channels
        "im:write",            # DMs
        "users:read", "users.profile:read"
    ]),
)
def post_message(
    context: ToolContext,
    channel_id: Annotated[str, "Slack channel ID (or DM ID)."],
    text: Annotated[str, "Message text to post."],
    thread_ts: Annotated[Optional[str], "Parent message ts to reply in-thread"] = None,
) -> Annotated[str, "Timestamp (ts) of the posted message"]:
    """Send a message to a channel or thread."""
    client = WebClient(token=context.authorization.token)
    try:
        resp = client.chat_postMessage(channel=channel_id, text=text, thread_ts=thread_ts)
        return resp["ts"]
    except SlackApiError as e:
        raise RetryableToolError("Slack API error", developer_message=str(e))


# --- Fetch last N messages ------------------------------------------
@tool(
    name="Slack.FetchMessages",
    description="Fetch the last N messages from a channel.",
    requires_auth=Slack(scopes=[
        "channels:history", "groups:history", "im:history", "mpim:history"
    ]),
)
def fetch_messages(
    context: ToolContext,
    channel_id: Annotated[str, "Slack channel ID to read from."],
    limit: Annotated[int, "How many messages to fetch (max 1000)."] = 50,
) -> Annotated[List[dict], "List of message objects"]:
    """Return recent channel messages (newest first)."""
    client = WebClient(token=context.authorization.token)
    resp = client.conversations_history(channel=channel_id, limit=limit)
    return resp.get("messages", [])


# --- Get user profile -----------------------------------------------
@tool(
    name="Slack.GetUserProfile",
    description="Get Slack user’s basic profile (email, real_name, id).",
    requires_auth=Slack(scopes=["users:read", "users.profile:read"]),
)
def get_user_profile(
    context: ToolContext,
    user_id: Annotated[str, "Slack user ID (e.g. U123...)."],
) -> Annotated[dict, "User profile info (email, real_name, id)."]:
    client = WebClient(token=context.authorization.token)
    info = client.users_info(user=user_id)
    user = info.get("user")
    if not user:
        raise RetryableToolError("User not found", developer_message=f"user_id={user_id}")
    profile = user.get("profile", {})
    return {
        "id": user.get("id"),
        "real_name": user.get("real_name"),
        "email": profile.get("email")
    }
