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
            "project": project_key,
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

    # Handle the response properly - check if it's a string or object
    if hasattr(res, 'output'):
        # If output is a string, return it directly
        if isinstance(res.output, str):
            return res.output
        
        # If output is a dict-like object, try to get the key
        if hasattr(res.output, 'get'):
            created_key = res.output.get("created_key") or res.output.get("key")
            if created_key:
                return created_key
        
        # If output is an object with attributes, try to access them
        if hasattr(res.output, 'created_key'):
            return res.output.created_key
        if hasattr(res.output, 'key'):
            return res.output.key
        
        # If none of the above work, return the string representation
        return str(res.output)
    
    # If no output attribute, return the string representation
    return str(res)
