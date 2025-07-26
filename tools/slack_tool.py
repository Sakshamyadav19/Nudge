# tools/slack_arcade_tool.py

import os
from arcadepy import Arcade
from dotenv import load_dotenv

load_dotenv()

# ——— Setup Arcade client & authorize once ———
client = Arcade(api_key=os.getenv("ARCADE_API_KEY"))
USER_ID = os.getenv("ARCADE_USER_ID")

auth = client.tools.authorize(
    tool_name="Slack.SendMessage",
    user_id=USER_ID
)

if auth.status != "completed":
    print("Please visit this URL to authorize the Slack connector:")
    print(auth.url)
    auth = client.auth.wait_for_completion(auth)

if auth.status != "completed":
    raise RuntimeError("🛑 Slack authorization failed — cannot proceed.")

print(f"✅ Slack tool authorized for user: {auth.user_id}")

# ——— Tool functions ———
def slack_post_message(
    channel_id: str,
    text: str,
    thread_ts: str = None
) -> str:
    """
    Post a message to a Slack channel (or thread) via Arcade and return the timestamp.
    Raises RuntimeError on failure.

    Args:
        channel_id: The Slack channel ID (or DM ID).
        text: Message text to post.
        thread_ts: Parent message ts to reply in-thread (optional).
    """
    payload = {
        "conversation_id": channel_id,
        "text": text
    }
    
    if thread_ts:
        payload["thread_ts"] = thread_ts

    res = client.tools.execute(
        tool_name="Slack.SendMessage",
        input=payload,
        user_id=USER_ID,
    )

    if not res.success:
        code = getattr(res, "error_code", None)
        msg = getattr(res, "error_message", str(res))
        raise RuntimeError(f"Arcade tool call failed [{code}]: {msg}")

    api_error = res.output.get("error")
    if api_error:
        raise RuntimeError(f"Slack API error: {api_error}")

    return res.output.get("ts", "")


def slack_fetch_messages(
    channel_id: str,
    limit: int = 50
) -> list:
    """
    Fetch the last N messages from a Slack channel via Arcade.
    Raises RuntimeError on failure.

    Args:
        channel_id: The Slack channel ID to read from.
        limit: How many messages to fetch (max 1000).
    """
    res = client.tools.execute(
        tool_name="Slack.FetchMessages@1.0.0",
        input={
            "conversation_id": channel_id,
            "limit": limit
        },
        user_id=USER_ID,
    )

    if not res.success:
        code = getattr(res, "error_code", None)
        msg = getattr(res, "error_message", str(res))
        raise RuntimeError(f"Arcade tool call failed [{code}]: {msg}")

    api_error = res.output.get("error")
    if api_error:
        raise RuntimeError(f"Slack API error: {api_error}")

    return res.output.get("messages", [])


def slack_get_user_profile(user_id: str) -> dict:
    """
    Get Slack user's basic profile via Arcade.
    Raises RuntimeError on failure.

    Args:
        user_id: Slack user ID (e.g. U123...).
    """
    res = client.tools.execute(
        tool_name="Slack.Slack.GetUsersInfo",
        input={
            "user_id": user_id
        },
        user_id=USER_ID,
    )

    if not res.success:
        code = getattr(res, "error_code", None)
        msg = getattr(res, "error_message", str(res))
        raise RuntimeError(f"Arcade tool call failed [{code}]: {msg}")

    api_error = res.output.get("error")
    if api_error:
        raise RuntimeError(f"Slack API error: {api_error}")

    return res.output


def slack_get_channel_info(channel_id: str) -> dict:
    """
    Get Slack channel info via Arcade.
    Raises RuntimeError on failure.

    Args:
        channel_id: Slack channel ID.
    """
    res = client.tools.execute(
        tool_name="Slack.GetConversationMetadata",
        input={
            "conversation_id": channel_id
        },
        user_id=USER_ID,
    )

    if not res.success:
        code = getattr(res, "error_code", None)
        msg = getattr(res, "error_message", str(res))
        raise RuntimeError(f"Arcade tool call failed [{code}]: {msg}")

    api_error = res.output.get("error")
    if api_error:
        raise RuntimeError(f"Slack API error: {api_error}")

    return res.output 