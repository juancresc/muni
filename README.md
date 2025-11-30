# Muni

A minimal LLM-powered coding agent with tool use.

## Installation

```bash
pip install -e .
```

## Usage

```bash
muni
```

Or:

```bash
PYTHONPATH=src python -m muni.cli
```

## Environment Variables

- `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` - API key for your provider
- `MODEL` - Model to use (default: `anthropic/claude-sonnet-4-20250514`)
- `SESSION_ID` - Optional session identifier for logs

## Features

- Multi-provider support (OpenAI, Anthropic)
- Streaming responses
- MDX-style tool calls (ReadFile, ListDir)
- Session logging

## How Tools Work

The agent uses MDX-style XML tags to call tools:

```
<ReadFile path="src/main.py" />
<ListDir path="." />
```

## Python API

```python
from muni import Agent, CLAUDE_SONNET

agent = Agent(
    session_id="my-session",
    model=CLAUDE_SONNET,
    system_prompt="You are a helpful assistant.",
)

# Streaming
for chunk in agent.stream("Hello!"):
    print(chunk, end="")
```
