"""
Chat export format parsers.

Parsers convert platform-specific export formats into Entrain's
normalized data model.
"""

from entrain.parsers.base import BaseParser, ParserRegistry
from entrain.parsers.chatgpt import ChatGPTParser
from entrain.parsers.claude import ClaudeParser
from entrain.parsers.characterai import CharacterAIParser
from entrain.parsers.generic import GenericParser

__all__ = [
    "BaseParser",
    "ParserRegistry",
    "ChatGPTParser",
    "ClaudeParser",
    "CharacterAIParser",
    "GenericParser",
]


def get_default_registry() -> ParserRegistry:
    """
    Create a ParserRegistry with all available parsers.

    Parsers are registered in order of specificity:
    1. ChatGPT - most specific format
    2. Claude - specific format with variations
    3. CharacterAI - specific format with variations
    4. Generic - fallback for any CSV/JSON (registered last)

    Returns:
        ParserRegistry with all parsers registered
    """
    registry = ParserRegistry()
    registry.register(ChatGPTParser())
    registry.register(ClaudeParser())
    registry.register(CharacterAIParser())
    registry.register(GenericParser())  # Generic is last (fallback)
    return registry
