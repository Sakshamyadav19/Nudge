# tools/jira_arcade_tool.py

import os
from arcadepy import Arcade

# ——— Setup Arcade client & authorize once ———
client = Arcade(api_key=os.getenv("ARCADE_API_KEY"))
USER_ID = os.getenv("ARCADE_USER_ID")

auth = client.tools.authorize(
    tool_name="Jira.CreateIssue@2.0.0",
    user_id=USER_ID
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
        project_key: The Jira project key (e.g., 'NDG').
        summary: A brief summary or short description.
        description: Detailed description of the issue.
        issue_type: One of 'Task', 'Bug', 'Story'. Defaults to 'Task'.
    """
    res = client.tools.execute(
        tool_name="Jira.CreateIssue@2.0.0",
        input={
            "title":       title,
            "project_key": project_key,
            "summary":     summary,
            "description": description,
            "issue_type":  issue_type,
        },
        user_id=USER_ID,
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
