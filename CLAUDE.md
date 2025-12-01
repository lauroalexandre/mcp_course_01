# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an MCP (Model Control Protocol) Course project that implements a CLI chat application using Google Gemini as the LLM provider. The project demonstrates MCP architecture with document management capabilities, tool usage, and prompt-based interactions.

**Key Architecture:**
- **MCP Server** (`cli_project/mcp_server.py`): FastMCP-based server exposing tools and resources for document management
- **MCP Client** (`cli_project/mcp_client.py`): Client wrapper for connecting to MCP servers with async context management
- **Gemini Integration** (`cli_project/core/gemini.py`): Adapter layer that wraps Google Gemini API to provide a unified interface
- **Chat System** (`cli_project/core/chat.py`, `cli_project/core/cli_chat.py`): Core chat logic with tool execution and resource handling
- **CLI Interface** (`cli_project/core/cli.py`): Interactive prompt-toolkit-based CLI with auto-completion for commands and document references

## Environment Setup

### Required Environment Variables (.env file)

```
GEMINI_MODEL="gemini-2.5-flash"  # The Gemini model to use
GOOGLE_API_KEY=""                # Your Google API key
USE_UV="0"                       # Set to "1" to use uv, "0" to use python directly
```

### Dependencies Installation

**Using uv (recommended):**
```bash
uv venv
.venv\Scripts\activate  # Windows
uv pip install -e .
```

**Without uv:**
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install google-generativeai python-dotenv prompt-toolkit "mcp[cli]==1.8.0"
```

## Running the Application

### Validation Test (Run this first)
```bash
python test_basic.py
```
This validates that all modules are correctly imported and configured.

### Main Application
```bash
# With uv
uv run main.py

# Without uv
python main.py
```

**IMPORTANT**: The CLI application requires a real terminal (cmd.exe or PowerShell on Windows). It will NOT work in Claude Code's simulated terminal due to `prompt_toolkit` requirements.

### Testing Gemini Integration
```bash
python test_gemini.py
```

### Listing Available Gemini Models
```bash
python list_models.py
```

## Development Notes

### Recent Fixes

**Fixed Issues:**
1. **mcp_server.py:17** - Changed `@mcp(...)` to `@mcp.tool(...)` to fix `TypeError: 'FastMCP' object is not callable`
2. **core/tools.py** - Removed dependency on `anthropic` module by:
   - Creating local `ToolResultBlockParam` TypedDict
   - Changing `Message` type to `Any` for generic message handling
   - Added support for both dict and object formats in tool request extraction

### MCP Server Implementation

The MCP server uses FastMCP and currently has incomplete TODOs in `mcp_server.py`:
- Resource to return all doc IDs
- Resource to return contents of a particular doc
- Prompt to rewrite a doc in markdown format
- Prompt to summarize a doc

**Decorator Usage:**
- Use `@mcp.tool()` for tools
- Use `@mcp.resource()` for resources
- Use `@mcp.prompt()` for prompts

### MCP Client Implementation

The MCP client has incomplete TODOs in `mcp_client.py`:
- `list_tools()`: Should return list of tools from MCP server
- `call_tool()`: Should execute a tool and return result
- `list_prompts()`: Should return list of prompts from MCP server
- `get_prompt()`: Should retrieve a specific prompt
- `read_resource()`: Should read and parse a resource

### Gemini Adapter Pattern

The `Gemini` class in `core/gemini.py` adapts the Google Gemini API to match the expected interface:
- Message format conversion between generic format and Gemini's format
- The `GeminiMessage` wrapper class provides compatibility
- Note: Gemini doesn't natively support tools in the same format as Claude, so tool functionality may be limited

### CLI Features

The CLI (`core/cli.py`) provides:
- **Command completion**: Type `/` to see available commands from MCP prompts
- **Document references**: Type `@` to reference documents (auto-completes available doc IDs)
- **Interactive suggestions**: Auto-suggests command arguments based on prompt definitions

### Windows Compatibility

The `main.py` includes Windows-specific event loop policy:
```python
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
```

This is required for proper stdio communication with MCP servers on Windows.

## Project Structure

```
cli_project/
├── core/
│   ├── gemini.py      # Gemini API adapter
│   ├── chat.py        # Base chat logic with tool execution
│   ├── cli_chat.py    # CLI-specific chat with resource/command handling
│   ├── cli.py         # Interactive CLI interface
│   └── tools.py       # Tool management and execution
├── mcp_server.py      # MCP server with document tools
├── mcp_client.py      # MCP client wrapper
├── main.py            # Application entry point
└── test_gemini.py     # Gemini integration test
```

## Common Workflows

### Adding New Documents
Edit the `docs` dictionary in `mcp_server.py`:
```python
docs = {
    "new_doc.md": "Content here",
}
```

### Testing MCP Client Connection
The `mcp_client.py` includes a test main function. Run with:
```bash
python mcp_client.py
```

### Using Document References in Chat
In the CLI, type `@` followed by a document ID (e.g., `@deposition.md`) to include document content in your query.

### Using Commands
Commands are MCP prompts. Type `/` in the CLI to see available commands. Example:
```
> /summarize deposition.md
```

## Important Implementation Details

1. **Async Context Management**: The application uses `AsyncExitStack` to properly manage multiple MCP client connections.

2. **Message Format**: Messages follow a generic format with `role` and `content` fields, which are converted to Gemini's format (with `parts` instead of `content`).

3. **Tool Execution Loop**: The chat system implements a loop that continues until the model stops requesting tools (see `chat.py:24-46`).

4. **Resource Extraction**: The `cli_chat.py` extracts `@mentions` from user queries and fetches corresponding document content from resources.

5. **Command Processing**: Commands starting with `/` are processed as MCP prompts, which are converted to message parameters and added to the conversation.
