import json
from typing import Tuple, Generator, Optional
from pathlib import Path
from datetime import datetime
import anthropic
from openai import OpenAI
from tools import ToolsManager

# Model constants (format: provider/model-name)
GPT_4O = "openai/gpt-4o"
GPT_4O_MINI = "openai/gpt-4o-mini"
GPT_4_TURBO = "openai/gpt-4-turbo"
O1 = "openai/o1"
O1_MINI = "openai/o1-mini"
O3_MINI = "openai/o3-mini"

CLAUDE_SONNET = "anthropic/claude-sonnet-4-20250514"
CLAUDE_OPUS = "anthropic/claude-opus-4-20250514"
CLAUDE_3_5_SONNET = "anthropic/claude-3-5-sonnet-20241022"
CLAUDE_3_5_HAIKU = "anthropic/claude-3-5-haiku-20241022"


class Agent:

    def __init__(self, session_id: str, model: str = GPT_4O, system_prompt: str = "", base_dir: Path = None):
        self.session_id = session_id
        self.provider, self.model_name = self._parse_model(model)
        self.model = model  # Keep full model string for logging
        self.system_prompt = system_prompt
        self.client = self._create_client()
        self.messages = [{"role": "system", "content": system_prompt}]
        self.tools = ToolsManager(base_dir or Path.cwd())
        # Log the initial system message
        self._log_message(self.messages[0])

    @staticmethod
    def _parse_model(model: str) -> Tuple[str, str]:
        """
        Parse provider and model name from model string.
        
        Args:
            model: Model string in format "provider/model-name"
            
        Returns:
            Tuple of (provider, model_name)
            
        Raises:
            ValueError: If model string is not in correct format
        """
        if "/" not in model:
            raise ValueError(
                f"Invalid model format: '{model}'. "
                f"Expected format: 'provider/model-name' (e.g., 'openai/gpt-4o')"
            )
        
        parts = model.split("/", 1)
        provider = parts[0].lower()
        model_name = parts[1]
        
        if provider not in ("openai", "anthropic"):
            raise ValueError(f"Unknown provider: '{provider}'. Supported: openai, anthropic")
        
        return provider, model_name

    def _create_client(self):
        """Create the appropriate client based on provider."""
        if self.provider == "openai":
            return OpenAI()
        elif self.provider == "anthropic":
            return anthropic.Anthropic()
        else:
            raise ValueError(f"Unknown provider: {self.provider}")

    def _log_message(self, message):
        """
        Log a message to the session log file.
        
        Args:
            message: The message dictionary to log
        """
        try:
            # Create logs directory if it doesn't exist
            logs_dir = Path("logs")
            logs_dir.mkdir(exist_ok=True)
            
            # Prepare log entry
            log_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "session_id": self.session_id,
                "role": message.get("role"),
                "content": message.get("content"),
            }
            
            # Add model info for assistant messages
            if message.get("role") == "assistant":
                log_entry["model"] = self.model
            
            # Append to log file
            log_file = logs_dir / f"{self.session_id}.jsonl"
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
                
        except Exception as e:
            # Don't crash if logging fails
            print(f"Warning: Failed to log message: {e}")

    def _add_user_message(self, content):
        """Add a user message to the conversation."""
        m = {"content": content, "role": "user"}
        self.messages.append(m)
        self._log_message(m)
        return m

    def _add_assistant_message(self, content):
        """Add an assistant message to the conversation."""
        m = {"content": content, "role": "assistant"}
        self.messages.append(m)
        self._log_message(m)
        return m

    def _add_system_message(self, content):
        """Add a system message to the conversation (e.g., tool results)."""
        m = {"content": content, "role": "system"}
        self.messages.append(m)
        self._log_message(m)
        return m

    def _process_tools(self, content: str) -> Optional[str]:
        """Process tool calls in content. Returns formatted results or None."""
        results = self.tools.process(content)
        if results:
            return self.tools.format_results(results)
        return None

    def _handle_openai(self, stream: bool = False):
        """Handle OpenAI API call."""
        completion = self.client.chat.completions.create(
            model=self.model_name,
            messages=self.messages,
            stream=stream,
        )
        
        if stream:
            return completion
        
        if not completion.choices or len(completion.choices) == 0:
            return None
        
        return completion.choices[0].message.content

    def _stream_openai(self) -> Generator[str, None, str]:
        """Stream OpenAI response, yielding chunks. Returns full content."""
        stream = self._handle_openai(stream=True)
        full_content = []
        
        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                text = chunk.choices[0].delta.content
                full_content.append(text)
                yield text
        
        return "".join(full_content)

    def _get_anthropic_messages(self) -> Tuple[list, str]:
        """Prepare messages for Anthropic API."""
        anthropic_messages = [
            {"role": m["role"], "content": m["content"]}
            for m in self.messages
            if m["role"] != "system"
        ]
        system_content = "\n\n".join(
            m["content"] for m in self.messages if m["role"] == "system"
        )
        return anthropic_messages, system_content

    def _handle_anthropic(self) -> str:
        """Handle Anthropic API call."""
        anthropic_messages, system_content = self._get_anthropic_messages()
        
        response = self.client.messages.create(
            model=self.model_name,
            max_tokens=8192,
            system=system_content,
            messages=anthropic_messages,
        )
        
        if not response.content:
            return None
        
        text_parts = [
            block.text for block in response.content 
            if hasattr(block, 'text')
        ]
        return "".join(text_parts) if text_parts else None

    def _stream_anthropic(self) -> Generator[str, None, str]:
        """Stream Anthropic response, yielding chunks. Returns full content."""
        anthropic_messages, system_content = self._get_anthropic_messages()
        full_content = []
        
        with self.client.messages.stream(
            model=self.model_name,
            max_tokens=8192,
            system=system_content,
            messages=anthropic_messages,
        ) as stream:
            for text in stream.text_stream:
                full_content.append(text)
                yield text
        
        return "".join(full_content)

    def handle(self, user_message: str = None) -> list:
        """Handle a conversation turn (non-streaming)."""
        if user_message:
            self._add_user_message(user_message)
        
        if self.provider == "openai":
            content = self._handle_openai()
        elif self.provider == "anthropic":
            content = self._handle_anthropic()
        else:
            raise ValueError(f"Unknown provider: {self.provider}")
        
        new_messages = []
        if content:
            new_messages.append(self._add_assistant_message(content))
            # Process tools and add results if any
            tool_results = self._process_tools(content)
            if tool_results:
                new_messages.append(self._add_system_message(f"[Tool Results]\n{tool_results}"))
        
        return new_messages

    def stream(self, user_message: str = None) -> Generator[str, None, Optional[str]]:
        """Stream a conversation turn, yielding text chunks. Returns tool results if any."""
        if user_message:
            self._add_user_message(user_message)
        
        if self.provider == "openai":
            gen = self._stream_openai()
        elif self.provider == "anthropic":
            gen = self._stream_anthropic()
        else:
            raise ValueError(f"Unknown provider: {self.provider}")
        
        full_content = []
        for chunk in gen:
            full_content.append(chunk)
            yield chunk
        
        # Log the complete message after streaming
        content = "".join(full_content)
        if content:
            self._add_assistant_message(content)
            # Process tools and add results if any
            tool_results = self._process_tools(content)
            if tool_results:
                self._add_system_message(f"[Tool Results]\n{tool_results}")
                return tool_results
        return None
