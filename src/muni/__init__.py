"""Agent4 - A minimal LLM-powered coding agent with tool use."""

from .agent import Agent
from .agent import (
    GPT_4O,
    GPT_4O_MINI,
    GPT_4_TURBO,
    O1,
    O1_MINI,
    O3_MINI,
    CLAUDE_SONNET,
    CLAUDE_OPUS,
    CLAUDE_3_5_SONNET,
    CLAUDE_3_5_HAIKU,
)

__version__ = "0.1.0"
__all__ = [
    "Agent",
    "GPT_4O",
    "GPT_4O_MINI", 
    "GPT_4_TURBO",
    "O1",
    "O1_MINI",
    "O3_MINI",
    "CLAUDE_SONNET",
    "CLAUDE_OPUS",
    "CLAUDE_3_5_SONNET",
    "CLAUDE_3_5_HAIKU",
]

