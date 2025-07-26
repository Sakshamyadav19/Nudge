# LlamaIndex Migration: AgentGraph to ReActAgent

This project has been updated to use the current LlamaIndex API structure, migrating from the deprecated `AgentGraph` to the modern `ReActAgent`.

## Changes Made

### 1. Updated `agent.py`
- **Removed**: `AgentGraph`, `ToolNode`, `SimpleRouter` imports
- **Added**: `ReActAgent`, `FunctionTool` imports
- **Replaced**: Complex graph-based routing with simple function tools
- **Improved**: Better error handling and fallback mechanisms

### 2. New Agent Structure

#### Before (AgentGraph):
```python
from llama_index.agent import AgentGraph, ToolNode, SimpleRouter

router = SimpleRouter(decide_fn=lambda q: classify_action(q["text"]))
nodes = {
    "jira": ToolNode(func=lambda q: create_jira_ticket(q["text"], q["slack_user"])),
    "calendar": ToolNode(func=lambda q: "Calendar functionality coming soon"),
    "noop": ToolNode(func=lambda q: "No action needed")
}
graph = AgentGraph(nodes=nodes, router=router)
mcp_agent = graph.as_agent(llm=llm)
```

#### After (ReActAgent):
```python
from llama_index.agent import ReActAgent
from llama_index.tools import FunctionTool

jira_tool = FunctionTool.from_defaults(
    fn=create_jira_ticket,
    name="create_jira_ticket",
    description="Create a Jira ticket for a task or issue mentioned in Slack"
)

tools = [jira_tool, calendar_tool]
agent = ReActAgent.from_tools(tools, llm=llm, verbose=True)
```

### 3. Enhanced Functionality

#### Two Processing Modes:
1. **LLM Agent Mode** (`process_message_with_context`):
   - Uses ReActAgent with conversation context
   - More intelligent decision making
   - Requires OpenAI API key

2. **Simple Mode** (`process_message_simple`):
   - Keyword-based classification
   - Fast and reliable fallback
   - No LLM dependency

## Benefits of the Migration

### 1. **Modern API**
- Uses current LlamaIndex best practices
- Better compatibility with future versions
- Improved performance and reliability

### 2. **Simpler Architecture**
- Removed complex graph routing
- Direct function tool integration
- Easier to understand and maintain

### 3. **Better Error Handling**
- Graceful fallback to simple processing
- Clear error messages
- Robust exception handling

### 4. **Enhanced Flexibility**
- Easy to add new tools
- Better tool descriptions for LLM
- More natural language processing

## Testing

### Run Agent Tests:
```bash
python test_agent.py
```

This will test both processing modes with sample messages.

### Expected Output:
```
🧪 Testing agent functionality...

1. Testing: 'Please create a task for me to review the documentation'
   Simple result: Action: jira, Result: Ticket PROJ-123 created successfully
   LLM result: I'll create a Jira ticket for you to review the documentation...

2. Testing: 'Can you schedule a meeting for tomorrow?'
   Simple result: Action: calendar, Result: Calendar functionality coming soon
   LLM result: I'll help you schedule a meeting for tomorrow...

3. Testing: 'Hello, how are you?'
   Simple result: Action: noop, Result: No action needed
   LLM result: Hello! I'm here to help with tasks and scheduling...
```

## Troubleshooting

### Common Issues:

1. **"OpenAI API key not set"**
   - Set `OPENAI_API_KEY` in your `.env` file
   - LLM processing will fail, but simple processing will work

2. **"Module not found" errors**
   - Ensure all LlamaIndex packages are installed
   - Run: `pip install -r requirements.txt`

3. **"Tool execution failed"**
   - Check that Slack and Jira tools are properly configured
   - Verify environment variables are set correctly

### Fallback Behavior:
- If LLM processing fails, the system automatically falls back to simple keyword-based processing
- This ensures the bot remains functional even if there are API issues

## Migration Notes

- **Backward Compatible**: All existing API endpoints remain the same
- **No Breaking Changes**: The `process_message_with_context` function signature is unchanged
- **Enhanced Features**: Better conversation context handling and tool descriptions
- **Improved Reliability**: Multiple fallback mechanisms ensure system stability

The migration maintains all existing functionality while providing a more robust and maintainable codebase. 