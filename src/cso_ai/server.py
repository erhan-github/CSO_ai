"""
CSO.ai MCP Server - Your AI Chief Strategy Officer.

This module implements the stdio-based MCP server that responds to tool calls
from Cursor and other MCP-compatible clients.
"""

import asyncio
import logging
import os
from pathlib import Path
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    GetPromptResult,
    Prompt,
    PromptArgument,
    PromptMessage,
    TextContent,
    Tool,
)

from cso_ai.tools_refined import TOOLS, handle_tool_call


def load_env_file() -> None:
    """Load environment variables from .env file."""
    # Check multiple possible locations (in priority order)
    possible_paths = [
        # Project root (cso-ai/.env) - most likely location
        Path(__file__).parent.parent.parent / ".env",
        # Current working directory
        Path.cwd() / ".env",
        # Parent of cwd (if running from src/)
        Path.cwd().parent / ".env",
        # User config directory
        Path.home() / ".cso-ai" / ".env",
    ]

    for env_path in possible_paths:
        env_path = env_path.resolve()
        if env_path.exists():
            try:
                with open(env_path) as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            key, value = line.split("=", 1)
                            key = key.strip()
                            value = value.strip().strip("'\"")
                            if key and value and key not in os.environ:
                                os.environ[key] = value
                break  # Use first found .env
            except Exception:
                continue


# Load environment variables before anything else
load_env_file()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("cso-ai")

# Create MCP server instance
server = Server("cso-ai")

# Define prompts - simplified for 3 core tools
PROMPTS: list[Prompt] = [
    Prompt(
        name="read",
        description="Get top articles for your stack - 'What should I read?'",
        arguments=[],
    ),
    Prompt(
        name="strategy",
        description="Get strategic advice - 'What should I focus on?'",
        arguments=[
            PromptArgument(
                name="context",
                description="Optional context about what you're working on",
                required=False,
            ),
        ],
    ),
]


@server.list_tools()
async def list_tools() -> list[Tool]:
    """Return the list of available tools."""
    return TOOLS


@server.list_prompts()
async def list_prompts() -> list[Prompt]:
    """Return the list of available prompts."""
    return PROMPTS


@server.get_prompt()
async def get_prompt(name: str, arguments: dict[str, str] | None) -> GetPromptResult:
    """Handle prompt requests - simplified for 3 core tools."""
    args = arguments or {}

    prompt_handlers = {
        "read": lambda: GetPromptResult(
            description="Top articles for your stack",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text="CSO, what should I read?",
                    ),
                ),
            ],
        ),
        "strategy": lambda: GetPromptResult(
            description=f"Strategic advice{' for ' + args.get('context') if args.get('context') else ''}",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"CSO, what should I focus on?{' Context: ' + args.get('context') if args.get('context') else ''}",
                    ),
                ),
            ],
        ),
    }

    handler = prompt_handlers.get(name)
    if handler:
        return handler()

    return GetPromptResult(
        description="CSO.ai - Instant Strategic Intelligence",
        messages=[
            PromptMessage(
                role="user",
                content=TextContent(type="text", text="CSO, what should I read?"),
            ),
        ],
    )


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any] | None) -> list[TextContent]:
    """Handle tool calls from the MCP client."""
    logger.info(f"CSO.ai tool invoked: {name} with args: {arguments}")

    try:
        result = await handle_tool_call(name, arguments or {})
        return [TextContent(type="text", text=result)]
    except Exception as err:
        logger.error(f"Error in tool {name}: {err}", exc_info=True)
        return [TextContent(type="text", text=f"CSO.ai Error: {str(err)}")]


async def run_server() -> None:
    """Run the CSO.ai MCP server."""
    logger.info("🧠 CSO.ai starting up...")

    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


def main() -> None:
    """Main entry point for cso-ai command."""
    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        logger.info("CSO.ai shutting down...")
    except Exception as err:
        logger.error(f"CSO.ai error: {err}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
