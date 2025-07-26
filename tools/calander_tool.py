# tools/calendar_arcade_tool.py

import os
from arcadepy import Arcade

# ——— Setup Arcade client & authorize once ———
client = Arcade(api_key=os.getenv("ARCADE_API_KEY"))
USER_ID = os.getenv("ARCADE_USER_ID")

auth = client.tools.authorize(
    tool_name="GoogleCalendar.CreateEvent@3.0.0",
    user_id=USER_ID
)

if auth.status != "completed":
    print("Please visit this URL to authorize the Google Calendar connector:")
    print(auth.url)
    auth = client.auth.wait_for_completion(auth)

if auth.status != "completed":
    raise RuntimeError("🛑 Google Calendar authorization failed — cannot proceed.")

print(f"✅ Google Calendar tool authorized for user: {auth.user_id}")

# ——— Tool function ———
def create_calendar_event(
    calendar_id: str,
    summary: str,
    description: str,
    start_datetime: str,
    end_datetime: str,
    timezone: str = "UTC"
) -> dict:
    """
    Create a calendar event via Arcade and return the event details.
    Raises RuntimeError on failure.

    Args:
        calendar_id: ID of the calendar (e.g., 'primary').
        summary: Brief title for the event.
        description: Detailed description.
        start_datetime: ISO 8601 start (e.g. '2025-07-28T15:00:00-07:00').
        end_datetime: ISO 8601 end (e.g. '2025-07-28T16:00:00-07:00').
        timezone: IANA timezone (default 'UTC').
    """
    payload = {
        "calendar_id":  calendar_id,
        "summary":      summary,
        "description":  description,
        "start_datetime": start_datetime,
        "end_datetime":   end_datetime,
        "timezone":     timezone
    }

    res = client.tools.execute(
        tool_name="GoogleCalendar.CreateEvent@3.0.0",
        input=payload,
        user_id=USER_ID,
    )

    # Arcade execution errors
    if not res.success:
        code = getattr(res, "error_code", None)
        msg  = getattr(res, "error_message", str(res))
        raise RuntimeError(f"Arcade tool call failed [{code}]: {msg}")

    # API-level errors
    api_error = res.output.get("error")
    if api_error:
        raise RuntimeError(f"Google Calendar API error: {api_error}")

    # Successful response contains event details under res.output
    return res.output
