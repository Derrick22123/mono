"""Agno Agent factory — v1 guardrails: no db, tools, memory, or knowledge."""

from __future__ import annotations

from agno.agent import Agent
from agno.models.openai import OpenAIChat

TRADITIONAL_CHINESE_INSTRUCTIONS = "以繁體中文回覆。"


def create_agent(*, api_key: str | None, model_id: str) -> Agent:
    """Build the single chat agent without persistence or tools."""
    return Agent(
        name="chat",
        model=OpenAIChat(id=model_id, api_key=api_key),
        instructions=TRADITIONAL_CHINESE_INSTRUCTIONS,
    )
