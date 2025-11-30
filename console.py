#!/usr/bin/env python3
import os
import uuid
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

from llm import Agent, CLAUDE_SONNET

# Load environment variables
load_dotenv()

BASE_DIR: Path = Path(__file__).parent


def load_prompt(current_path: str) -> str:
    """Load system prompt from PROMPT.md and substitute variables."""
    prompt_path = BASE_DIR / "PROMPT.md"
    content = prompt_path.read_text(encoding="utf-8")
    return content.replace("{{ current_path }}", current_path)


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
    session_id: str = os.environ.get("SESSION_ID", str(uuid.uuid4()))
    model: str = os.environ.get("MODEL", CLAUDE_SONNET)
    
    print("=" * 50)
    print("Agent Console")
    print("=" * 50)
    print(f"Model: {model}")
    print(f"Session: {session_id}")
    print("Type 'exit' to quit, 'clear' to reset conversation")
    print("=" * 50)
    
    current_path: Path = Path(os.getcwd())
    system_prompt: str = load_prompt(str(current_path))
    agent: Agent = Agent(session_id=session_id, model=model, system_prompt=system_prompt, base_dir=current_path)
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
                agent = Agent(session_id=session_id, model=model, system_prompt=system_prompt, base_dir=current_path)
                print("✨ Conversation cleared\n")
                continue
            
            # Agent loop - process tools until [DONE] or no more tool calls
            iterations: int = 0
            message: Optional[str] = user_input
            
            while iterations < 50:
                iterations += 1
                content, tool_results = stream_response(agent, message)
                message = None  # Only pass user input on first iteration
                
                if "[DONE]" in content:
                    break
                
                print(f"📁 Tool Results:\n{tool_results}\n")
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except EOFError:
            print("\n\n👋 Goodbye!")
            break


if __name__ == "__main__":
    main()
