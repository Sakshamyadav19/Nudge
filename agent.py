# mcp_agent.py
import os
from llama_index.agent import AgentGraph, ToolNode, SimpleRouter
from llama_index.llms import OpenAI
from slack_tool import SlackTool
from jira_tool import JiraTool

# ─────────────── INIT TOOLS ───────────────
llm = OpenAI(model="gpt-4o")
slack_tool = SlackTool(os.environ["SLACK_BOT_TOKEN"])
jira_tool = JiraTool(
    base=os.environ["JIRA_BASE_URL"],
    email=os.environ["JIRA_EMAIL"],
    token=os.environ["JIRA_API_TOKEN"]
)

# ─────────────── WRAPPER FUNCTION ───────────────
def create_jira_ticket(text, slack_user):
    profile = slack_tool.user_profile(slack_user)
    email = profile["profile"]["email"]
    key = jira_tool.create_issue(
        project="PROJ",
        summary=text[:120],
        description=f"Raised from Slack:\n\n{text}",
        assignee_account_id=email
    )
    slack_tool.post(
        os.environ["SLACK_CHANNEL_ID"],
        f"🎫 Created Jira ticket `{key}` for task: {text}"
    )
    return f"Ticket {key} created"

# ─────────────── ROUTING LOGIC ───────────────
def classify_action(query: str) -> str:
    """
    Keyword-based router — replace with LLM-powered later if needed.
    """
    query_lower = query.lower()
    if "assign" in query_lower or "please" in query_lower or "task" in query_lower:
        return "jira"
    else:
        return "noop"

router = SimpleRouter(decide_fn=lambda q: classify_action(q["text"]))

# ─────────────── TOOL NODES ───────────────
nodes = {
    "jira": ToolNode(func=lambda q: create_jira_ticket(q["text"], q["slack_user"])),
    "noop": ToolNode(func=lambda q: "No action needed")
}

# ─────────────── BUILD AGENT GRAPH ───────────────
graph = AgentGraph(nodes=nodes, router=router)
mcp_agent = graph.as_agent(llm=llm)
