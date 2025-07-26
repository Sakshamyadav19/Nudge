# tools/jira_arcade_tool.py

import os
from arcadepy import Arcade
from dotenv import load_dotenv

load_dotenv()

# ——— Setup Arcade client & authorize once ———
ARCADE_API_KEY = os.getenv("ARCADE_API_KEY")
ARCADE_USER_ID = os.getenv("ARCADE_USER_ID")

if not ARCADE_API_KEY or not ARCADE_USER_ID:
    raise RuntimeError("🛑 ARCADE_API_KEY and ARCADE_USER_ID environment variables are required")

client = Arcade(api_key=ARCADE_API_KEY)

auth = client.tools.authorize(
    tool_name="Jira.CreateIssue",
    user_id=ARCADE_USER_ID
)

if auth.status != "completed":
    print("Please visit this URL to authorize the Jira connector:")
    print(auth.url)
    auth = client.auth.wait_for_completion(auth)

if auth.status != "completed":
    raise RuntimeError("🛑 Jira authorization failed — cannot proceed.")

print(f"✅ Jira tool authorized for user: {auth.user_id}")

# ——— Tool function ———
def jira_create_issue(
    title: str,
    project_key: str,
    summary: str,
    description: str,
    issue_type: str = "Task"
) -> str:
    """
    Create a Jira ticket via Arcade and return its issue key (e.g. 'PROJ-123').
    Raises RuntimeError on failure.

    Args:
        title: The human-readable title of the ticket.
        project_key: The Jira project key (e.g., 'PROJ').
        summary: A brief summary or short description.
        description: Detailed description of the issue.
        issue_type: One of 'Task', 'Bug', 'Story'. Defaults to 'Task'.
    """
    res = client.tools.execute(
        tool_name="Jira.CreateIssue",
        input={
            "title":       title,
            "project_key": project_key,
            "summary":     summary,
            "description": description,
            "issue_type":  issue_type,
        },
        user_id=ARCADE_USER_ID,
    )

    if not res.success:
        code = getattr(res, "error_code", None)
        msg  = getattr(res, "error_message", str(res))
        raise RuntimeError(f"Arcade tool call failed [{code}]: {msg}")

    api_error = res.output.get("error")
    if api_error:
        raise RuntimeError(f"Jira API error: {api_error}")

    created_key = res.output.get("created_key") or res.output.get("key")
    if not created_key:
        raise RuntimeError(f"Unexpected response from Jira: {res.output}")

    return created_key
