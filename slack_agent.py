# slack_agent.py
from typing import Annotated, Optional, List
from arcade_tdk import ToolContext, tool
from arcade_tdk.auth import Slack
from arcade_tdk.errors import RetryableToolError
from tools.slack_tool import slack_post_message, slack_fetch_messages, slack_get_user_profile


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
    try:
        return slack_post_message(channel_id=channel_id, text=text, thread_ts=thread_ts)
    except Exception as e:
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
    try:
        return slack_fetch_messages(channel_id=channel_id, limit=limit)
    except Exception as e:
        raise RetryableToolError("Slack API error", developer_message=str(e))


# --- Get user profile -----------------------------------------------
@tool(
    name="Slack.GetUserProfile",
    description="Get Slack user's basic profile (email, real_name, id).",
    requires_auth=Slack(scopes=["users:read", "users.profile:read"]),
)
def get_user_profile(
    context: ToolContext,
    user_id: Annotated[str, "Slack user ID (e.g. U123...)."],
) -> Annotated[dict, "User profile info (email, real_name, id)."]:
    try:
        return slack_get_user_profile(user_id=user_id)
    except Exception as e:
        raise RetryableToolError("Slack API error", developer_message=str(e))
