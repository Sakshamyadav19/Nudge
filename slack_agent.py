# slack_agent.py
from typing import Optional, List
from tools.slack_tool import slack_post_message, slack_fetch_messages, slack_get_user_profile, slack_get_channel_info


# --- Post a message -------------------------------------------------
def post_message(
    channel_id: str,
    text: str,
    thread_ts: Optional[str] = None,
) -> str:
    """
    Post a message to a Slack channel (or thread).
    
    Args:
        channel_id: Slack channel ID (or DM ID).
        text: Message text to post.
        thread_ts: Parent message ts to reply in-thread (optional).
    
    Returns:
        Timestamp (ts) of the posted message
    """
    try:
        return slack_post_message(channel_id=channel_id, text=text, thread_ts=thread_ts)
    except Exception as e:
        raise RuntimeError(f"Failed to post message: {str(e)}")


# --- Fetch last N messages ------------------------------------------
def fetch_messages(
    channel_id: str,
    limit: int = 50,
) -> List[dict]:
    """
    Fetch the last N messages from a channel.
    
    Args:
        channel_id: Slack channel ID to read from.
        limit: How many messages to fetch (max 1000).
    
    Returns:
        List of message objects (newest first).
    """
    try:
        return slack_fetch_messages(channel_id=channel_id, limit=limit)
    except Exception as e:
        raise RuntimeError(f"Failed to fetch messages: {str(e)}")


# --- Get user profile -----------------------------------------------
def get_user_profile(
    user_id: str,
) -> dict:
    """
    Get Slack user's basic profile (email, real_name, id).
    
    Args:
        user_id: Slack user ID (e.g. U123...).
    
    Returns:
        User profile info (email, real_name, id, etc.).
    """
    try:
        return slack_get_user_profile(user_id=user_id)
    except Exception as e:
        raise RuntimeError(f"Failed to get user profile: {str(e)}")


# --- Get channel info -----------------------------------------------
def get_channel_info(
    channel_id: str,
) -> dict:
    """
    Get Slack channel information.
    
    Args:
        channel_id: Slack channel ID.
    
    Returns:
        Channel information including members, name, etc.
    """
    try:
        return slack_get_channel_info(channel_id=channel_id)
    except Exception as e:
        raise RuntimeError(f"Failed to get channel info: {str(e)}")


# --- Convenience function for getting channel members --------------
def get_channel_members(channel_id: str) -> List[str]:
    """
    Get all member IDs in a Slack channel.
    
    Args:
        channel_id: Slack channel ID.
    
    Returns:
        List of user IDs who are members of the channel.
    """
    try:
        channel_info = slack_get_channel_info(channel_id=channel_id)
        return channel_info.get("members", [])
    except Exception as e:
        raise RuntimeError(f"Failed to get channel members: {str(e)}")
