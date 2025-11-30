#!/usr/bin/env python3
"""Command-line interface for Agent4."""

import os
import platform
import uuid
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

from .agent import Agent, CLAUDE_SONNET
from .tools import ToolsManager

# Load environment variables
load_dotenv()


def get_prompt_path() -> Path:
    """Get the path to PROMPT.md, checking multiple locations."""
    # Check current directory first
    local_prompt = Path.cwd() / "PROMPT.md"
    if local_prompt.exists():
        return local_prompt
    
    # Check package directory
    package_prompt = Path(__file__).parent / "PROMPT.md"
    if package_prompt.exists():
        return package_prompt
    
    raise FileNotFoundError("PROMPT.md not found")


def load_prompt(current_path: str, tools: ToolsManager) -> str:
    """Load system prompt from PROMPT.md and substitute variables."""
    prompt_path = get_prompt_path()
    content = prompt_path.read_text(encoding="utf-8")
    
    os_info = f"{platform.system()} {platform.release()}"
    tools_docs = tools.get_tools_documentation()
    
    content = content.replace("{{ current_path }}", current_path)
    content = content.replace("{{ os }}", os_info)
    content = content.replace("{{ tools }}", tools_docs)
    return content


def stream_response(agent: Agent, user_input: Optional[str] = None) -> tuple[str, Optional[str]]:
    """Stream and print assistant response. Returns (content, tool_results)."""
    print("\n🤖 Assistant:")
    full_content: list[str] = []
    tool_results: Optional[str] = None
    
    gen = agent.stream(user_input)
    # Manually iterate to capture the return value
    while True:
        try:
            chunk = next(gen)
            print(chunk, end="", flush=True)
            full_content.append(chunk)
        except StopIteration as e:
            tool_results = e.value
            break
    
    print("\n")
    return "".join(full_content), tool_results


def main() -> None:
    """Main entry point for the CLI."""
    session_id: str = str(uuid.uuid4())
    model: str = os.environ.get("MODEL", CLAUDE_SONNET)
    
    print("=" * 50)
    print("Agent4 Console")
    print("=" * 50)
    print(f"Model: {model}")
    print(f"Session: {session_id}")
    print("Type 'exit' to quit, 'clear' to reset conversation")
    print("=" * 50)
    
    current_path: Path = Path.cwd()
    tools: ToolsManager = ToolsManager(current_path)
    system_prompt: str = load_prompt(str(current_path), tools)
    agent: Agent = Agent(session_id=session_id, model=model, system_prompt=system_prompt, tools=tools)
    print("✅ Agent initialized\n")
    
    while True:
        try:
            user_input: str = input("👤 You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() == "exit":
                print("\n👋 Goodbye!")
                break
            
            if user_input.lower() == "clear":
                agent = Agent(session_id=session_id, model=model, system_prompt=system_prompt, tools=tools)
                print("✨ Conversation cleared\n")
                continue
            
            # Agent loop - process tools until no more tool calls
            iterations: int = 0
            message: Optional[str] = user_input
            
            while iterations < 500:
                iterations += 1
                content, tool_results = stream_response(agent, message)
                message = None  # Only pass user input on first iteration
                
                # If no tool results, we're done (agent didn't call any tools)
                if not tool_results:
                    break
                
                # Show tool results and continue (agent needs to see them)
                print(f"📁 Tool Results:\n{tool_results}\n")
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except EOFError:
            print("\n\n👋 Goodbye!")
            break


if __name__ == "__main__":
    main()

