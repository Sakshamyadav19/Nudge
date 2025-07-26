# tools/slack_tool.py

import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv

load_dotenv()

# ——— Setup Slack client ———
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")

if not SLACK_BOT_TOKEN:
    raise RuntimeError("🛑 SLACK_BOT_TOKEN environment variable is required")

client = WebClient(token=SLACK_BOT_TOKEN)

print(f"✅ Slack SDK client initialized with bot token")

# ——— Tool functions ———

def slack_post_message(
    channel_id: str,
    text: str,
    thread_ts: str = None
) -> str:
    """
    Post a message to a Slack channel (or thread) via Slack SDK and return the timestamp.
    Raises RuntimeError on failure.

    Args:
        channel_id: The Slack channel ID (or DM ID).
        text: Message text to post.
        thread_ts: Parent message ts to reply in-thread (optional).
    """
    try:
        response = client.chat_postMessage(
            channel=channel_id,
            text=text,
            thread_ts=thread_ts
        )
        
        if not response["ok"]:
            raise RuntimeError(f"Slack API error: {response.get('error', 'Unknown error')}")
        
        return response["ts"]
        
    except SlackApiError as e:
        raise RuntimeError(f"Slack API error: {e.response['error']}")
    except Exception as e:
        raise RuntimeError(f"Unexpected error posting message: {str(e)}")


def slack_fetch_messages(
    channel_id: str,
    limit: int = 50
) -> list:
    """
    Fetch the last N messages from a Slack channel via Slack SDK.
    Raises RuntimeError on failure.

    Args:
        channel_id: The Slack channel ID to read from.
        limit: How many messages to fetch (max 1000).
    """
    try:
        response = client.conversations_history(
            channel=channel_id,
            limit=limit
        )
        
        if not response["ok"]:
            raise RuntimeError(f"Slack API error: {response.get('error', 'Unknown error')}")
        
        messages = response["messages"]
        
        # Format messages to match expected structure
        formatted_messages = []
        for msg in messages:
            formatted_msg = {
                "ts": msg.get("ts", ""),
                "user": msg.get("user", ""),
                "text": msg.get("text", ""),
                "type": msg.get("type", "message"),
                "subtype": msg.get("subtype"),
                "bot_id": msg.get("bot_id"),
                "thread_ts": msg.get("thread_ts"),
                "reply_count": msg.get("reply_count"),
                "reply_users_count": msg.get("reply_users_count"),
                "latest_reply": msg.get("latest_reply"),
                "reply_users": msg.get("reply_users", []),
                "replies": msg.get("replies", [])
            }
            formatted_messages.append(formatted_msg)
        
        return formatted_messages
        
    except SlackApiError as e:
        raise RuntimeError(f"Slack API error: {e.response['error']}")
    except Exception as e:
        raise RuntimeError(f"Unexpected error fetching messages: {str(e)}")


def slack_get_user_profile(user_id: str) -> dict:
    """
    Get Slack user's basic profile via Slack SDK.
    Raises RuntimeError on failure.

    Args:
        user_id: Slack user ID (e.g. U123...).
    """
    try:
        response = client.users_info(user=user_id)
        
        if not response["ok"]:
            raise RuntimeError(f"Slack API error: {response.get('error', 'Unknown error')}")
        
        user = response["user"]
        
        # Format user profile to match expected structure
        profile = {
            "id": user.get("id", ""),
            "name": user.get("name", ""),
            "real_name": user.get("real_name", ""),
            "display_name": user.get("profile", {}).get("display_name", ""),
            "email": user.get("profile", {}).get("email", ""),
            "image_24": user.get("profile", {}).get("image_24", ""),
            "image_32": user.get("profile", {}).get("image_32", ""),
            "image_48": user.get("profile", {}).get("image_48", ""),
            "image_72": user.get("profile", {}).get("image_72", ""),
            "image_192": user.get("profile", {}).get("image_192", ""),
            "image_512": user.get("profile", {}).get("image_512", ""),
            "status_text": user.get("profile", {}).get("status_text", ""),
            "status_emoji": user.get("profile", {}).get("status_emoji", ""),
            "team_id": user.get("team_id", ""),
            "is_admin": user.get("is_admin", False),
            "is_owner": user.get("is_owner", False),
            "is_primary_owner": user.get("is_primary_owner", False),
            "is_restricted": user.get("is_restricted", False),
            "is_ultra_restricted": user.get("is_ultra_restricted", False),
            "is_bot": user.get("is_bot", False),
            "deleted": user.get("deleted", False),
            "real_name_normalized": user.get("real_name_normalized", ""),
            "display_name_normalized": user.get("profile", {}).get("display_name_normalized", ""),
            "profile": user.get("profile", {})
        }
        
        return profile
        
    except SlackApiError as e:
        raise RuntimeError(f"Slack API error: {e.response['error']}")
    except Exception as e:
        raise RuntimeError(f"Unexpected error getting user profile: {str(e)}")


def slack_get_channel_info(channel_id: str) -> dict:
    """
    Get Slack channel info via Slack SDK.
    Raises RuntimeError on failure.

    Args:
        channel_id: Slack channel ID.
    """
    try:
        response = client.conversations_info(channel=channel_id)
        
        if not response["ok"]:
            raise RuntimeError(f"Slack API error: {response.get('error', 'Unknown error')}")
        
        channel = response["channel"]
        
        # Format channel info to match expected structure
        channel_info = {
            "id": channel.get("id", ""),
            "name": channel.get("name", ""),
            "is_channel": channel.get("is_channel", False),
            "is_group": channel.get("is_group", False),
            "is_im": channel.get("is_im", False),
            "is_mpim": channel.get("is_mpim", False),
            "is_private": channel.get("is_private", False),
            "created": channel.get("created", 0),
            "creator": channel.get("creator", ""),
            "is_archived": channel.get("is_archived", False),
            "is_general": channel.get("is_general", False),
            "unlinked": channel.get("unlinked", 0),
            "name_normalized": channel.get("name_normalized", ""),
            "is_shared": channel.get("is_shared", False),
            "is_org_shared": channel.get("is_org_shared", False),
            "is_pending_ext_shared": channel.get("is_pending_ext_shared", False),
            "pending_shared": channel.get("pending_shared", []),
            "context_team_id": channel.get("context_team_id", ""),
            "updated": channel.get("updated", 0),
            "parent_conversation": channel.get("parent_conversation"),
            "conversation_host_id": channel.get("conversation_host_id", ""),
            "is_ext_shared": channel.get("is_ext_shared", False),
            "shared_team_ids": channel.get("shared_team_ids", []),
            "pending_connected_team_ids": channel.get("pending_connected_team_ids", []),
            "is_pending_shared": channel.get("is_pending_shared", False),
            "topic": channel.get("topic", {}),
            "purpose": channel.get("purpose", {}),
            "previous_names": channel.get("previous_names", []),
            "num_members": channel.get("num_members", 0),
            "members": channel.get("members", [])
        }
        
        return channel_info
        
    except SlackApiError as e:
        raise RuntimeError(f"Slack API error: {e.response['error']}")
    except Exception as e:
        raise RuntimeError(f"Unexpected error getting channel info: {str(e)}")


def slack_get_channel_members(channel_id: str) -> list:
    """
    Get all members of a Slack channel via Slack SDK.
    Raises RuntimeError on failure.

    Args:
        channel_id: Slack channel ID.
    """
    try:
        response = client.conversations_members(channel=channel_id)
        
        if not response["ok"]:
            raise RuntimeError(f"Slack API error: {response.get('error', 'Unknown error')}")
        
        return response["members"]
        
    except SlackApiError as e:
        raise RuntimeError(f"Slack API error: {e.response['error']}")
    except Exception as e:
        raise RuntimeError(f"Unexpected error getting channel members: {str(e)}") 