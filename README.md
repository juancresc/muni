# Agent4

A minimal LLM-powered coding agent with tool use.

## Features

- Multi-provider support (OpenAI, Anthropic)
- Streaming responses
- MDX-style tool calls (ReadFile, ListDir)
- Session logging

## How Tools Work

The agent uses MDX-style XML tags embedded in its responses to call tools:

```
<ReadFile path="src/main.py" />
<ListDir path="." recursive="true" />
```

## Usage

```bash
pip install -r requirements.txt
python console.py
```

## Environment Variables

- `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` - API key for your provider
- `MODEL` - Model to use (default: `anthropic/claude-sonnet-4-20250514`)
- `SESSION_ID` - Optional session identifier for logs

