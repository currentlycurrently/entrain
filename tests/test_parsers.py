"""
Tests for chat export parsers.

Tests basic parsing functionality for all supported platforms:
- ChatGPT
- Claude
- Character.AI
- Generic CSV/JSON
"""

import pytest
import json
import csv
from pathlib import Path
from datetime import datetime
from tempfile import NamedTemporaryFile, TemporaryDirectory
import zipfile

from entrain.parsers import (
    ChatGPTParser,
    ClaudeParser,
    CharacterAIParser,
    GenericParser,
    get_default_registry,
)
from entrain.models import Conversation, Corpus


# ============================================================================
# Claude Parser Tests
# ============================================================================


def test_claude_parser_can_parse_json():
    """Test Claude parser recognizes Claude JSON format."""
    parser = ClaudeParser()

    # Create temporary Claude-format JSON file
    with NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        claude_data = {
            "conversation_id": "test-123",
            "messages": [
                {"role": "user", "content": "Hello", "timestamp": 1234567890},
                {
                    "role": "assistant",
                    "content": "Hi there!",
                    "timestamp": 1234567895,
                },
            ],
        }
        json.dump(claude_data, f)
        temp_path = Path(f.name)

    try:
        assert parser.can_parse(temp_path)
    finally:
        temp_path.unlink()


def test_claude_parser_can_parse_jsonl():
    """Test Claude parser recognizes JSONL format."""
    parser = ClaudeParser()

    with NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
        f.write(
            json.dumps(
                {
                    "messages": [
                        {"role": "user", "content": "Test"},
                        {"role": "assistant", "content": "Response"},
                    ]
                }
            )
        )
        temp_path = Path(f.name)

    try:
        assert parser.can_parse(temp_path)
    finally:
        temp_path.unlink()


def test_claude_parser_parse_simple_json():
    """Test Claude parser can parse a simple conversation."""
    parser = ClaudeParser()

    with NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        claude_data = {
            "id": "conv-123",
            "title": "Test Conversation",
            "messages": [
                {
                    "role": "user",
                    "content": "What is 2+2?",
                    "timestamp": 1704110400,  # 2024-01-01 12:00:00
                },
                {
                    "role": "assistant",
                    "content": "2+2 equals 4.",
                    "timestamp": 1704110405,
                },
            ],
        }
        json.dump(claude_data, f)
        temp_path = Path(f.name)

    try:
        corpus = parser.parse(temp_path)

        assert isinstance(corpus, Corpus)
        assert len(corpus.conversations) == 1

        conv = corpus.conversations[0]
        assert conv.id == "conv-123"
        assert conv.source == "claude"
        assert len(conv.events) == 2
        assert conv.events[0].role == "user"
        assert conv.events[1].role == "assistant"
        assert "2+2" in conv.events[0].text_content
        assert "equals 4" in conv.events[1].text_content

    finally:
        temp_path.unlink()


def test_claude_parser_parse_message_array():
    """Test Claude parser can parse simple message array format."""
    parser = ClaudeParser()

    with NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "claude", "content": "Hi! How can I help?"},
            {"role": "human", "content": "What's the weather?"},
            {"role": "assistant", "content": "I don't have weather data."},
        ]
        json.dump(messages, f)
        temp_path = Path(f.name)

    try:
        corpus = parser.parse(temp_path)

        assert len(corpus.conversations) == 1
        conv = corpus.conversations[0]
        assert len(conv.events) == 4
        assert conv.events[0].role == "user"
        assert conv.events[1].role == "assistant"

    finally:
        temp_path.unlink()


# ============================================================================
# Character.AI Parser Tests
# ============================================================================


def test_characterai_parser_can_parse():
    """Test Character.AI parser recognizes Character.AI format."""
    parser = CharacterAIParser()

    with NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        cai_data = {
            "character_name": "Einstein",
            "description": "Albert Einstein",
            "greeting": "Hello! I am Einstein.",
            "histories": [
                [
                    {"is_human": True, "text": "What is relativity?"},
                    {"is_human": False, "text": "It's a theory about space and time."},
                ]
            ],
        }
        json.dump(cai_data, f)
        temp_path = Path(f.name)

    try:
        assert parser.can_parse(temp_path)
    finally:
        temp_path.unlink()


def test_characterai_parser_parse_with_histories():
    """Test Character.AI parser can parse histories format."""
    parser = CharacterAIParser()

    with NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        cai_data = {
            "character_name": "Socrates",
            "description": "Ancient Greek philosopher",
            "greeting": "Know thyself.",
            "histories": [
                [
                    {"is_human": True, "text": "What is wisdom?"},
                    {
                        "is_human": False,
                        "text": "Wisdom is knowing that you know nothing.",
                    },
                ]
            ],
        }
        json.dump(cai_data, f)
        temp_path = Path(f.name)

    try:
        corpus = parser.parse(temp_path)

        assert len(corpus.conversations) == 1
        conv = corpus.conversations[0]
        assert conv.source == "characterai"
        assert len(conv.events) == 2
        assert conv.events[0].role == "user"
        assert conv.events[1].role == "assistant"
        assert "wisdom" in conv.events[0].text_content.lower()
        assert conv.metadata["character_name"] == "Socrates"

    finally:
        temp_path.unlink()


def test_characterai_parser_parse_with_swipes():
    """Test Character.AI parser handles swipes (alternative responses)."""
    parser = CharacterAIParser()

    with NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        cai_data = {
            "character": "TestBot",
            "messages": [
                {"is_human": True, "text": "Hello"},
                {
                    "is_human": False,
                    "text": "",  # This will be overridden by swipes
                    "swipes": ["Response 1", "Response 2", "Response 3"],
                    "swipe_id": 1,  # Selected the second response
                },
            ],
        }
        json.dump(cai_data, f)
        temp_path = Path(f.name)

    try:
        corpus = parser.parse(temp_path)

        conv = corpus.conversations[0]
        assert len(conv.events) == 2
        # Should use the selected swipe (index 1 = "Response 2")
        assert conv.events[1].text_content == "Response 2"
        assert conv.events[1].metadata["swipe_count"] == 3

    finally:
        temp_path.unlink()


# ============================================================================
# Generic Parser Tests
# ============================================================================


def test_generic_parser_can_parse_csv():
    """Test Generic parser recognizes valid CSV format."""
    parser = GenericParser()

    with NamedTemporaryFile(mode="w", suffix=".csv", delete=False, newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["role", "content", "timestamp"])
        writer.writeheader()
        writer.writerow(
            {
                "role": "user",
                "content": "Hello",
                "timestamp": "2025-01-01 12:00:00",
            }
        )
        temp_path = Path(f.name)

    try:
        assert parser.can_parse(temp_path)
    finally:
        temp_path.unlink()


def test_generic_parser_can_parse_json():
    """Test Generic parser recognizes simple JSON message array."""
    parser = GenericParser()

    with NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
        ]
        json.dump(messages, f)
        temp_path = Path(f.name)

    try:
        assert parser.can_parse(temp_path)
    finally:
        temp_path.unlink()


def test_generic_parser_rejects_platform_specific():
    """Test Generic parser rejects platform-specific formats."""
    parser = GenericParser()

    # ChatGPT-specific format (has 'mapping')
    with NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        chatgpt_data = [
            {
                "role": "user",
                "content": "test",
                "mapping": {},  # ChatGPT-specific
            }
        ]
        json.dump(chatgpt_data, f)
        temp_path = Path(f.name)

    try:
        # Should reject this because it looks platform-specific
        assert not parser.can_parse(temp_path)
    finally:
        temp_path.unlink()


def test_generic_parser_parse_csv():
    """Test Generic parser can parse CSV conversations."""
    parser = GenericParser()

    with NamedTemporaryFile(mode="w", suffix=".csv", delete=False, newline="") as f:
        writer = csv.DictWriter(
            f, fieldnames=["conversation_id", "role", "content", "timestamp"]
        )
        writer.writeheader()
        writer.writerow(
            {
                "conversation_id": "chat1",
                "role": "user",
                "content": "What is AI?",
                "timestamp": "2025-01-01 10:00:00",
            }
        )
        writer.writerow(
            {
                "conversation_id": "chat1",
                "role": "assistant",
                "content": "AI is artificial intelligence.",
                "timestamp": "2025-01-01 10:00:05",
            }
        )
        temp_path = Path(f.name)

    try:
        corpus = parser.parse(temp_path)

        assert len(corpus.conversations) == 1
        conv = corpus.conversations[0]
        assert conv.id == "chat1"
        assert conv.source == "generic"
        assert len(conv.events) == 2
        assert conv.events[0].role == "user"
        assert conv.events[1].role == "assistant"

    finally:
        temp_path.unlink()


def test_generic_parser_parse_json_multiple_conversations():
    """Test Generic parser groups messages by conversation_id."""
    parser = GenericParser()

    with NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        messages = [
            {"conversation_id": "conv1", "role": "user", "content": "Hello"},
            {"conversation_id": "conv1", "role": "assistant", "content": "Hi"},
            {"conversation_id": "conv2", "role": "user", "content": "Test"},
            {"conversation_id": "conv2", "role": "assistant", "content": "Response"},
        ]
        json.dump(messages, f)
        temp_path = Path(f.name)

    try:
        corpus = parser.parse(temp_path)

        assert len(corpus.conversations) == 2
        conv_ids = {c.id for c in corpus.conversations}
        assert "conv1" in conv_ids
        assert "conv2" in conv_ids

    finally:
        temp_path.unlink()


def test_generic_parser_metadata_extraction():
    """Test Generic parser stores extra fields as metadata."""
    parser = GenericParser()

    with NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        messages = [
            {
                "role": "user",
                "content": "Test",
                "model": "gpt-4",
                "temperature": 0.7,
                "custom_field": "custom_value",
            }
        ]
        json.dump(messages, f)
        temp_path = Path(f.name)

    try:
        corpus = parser.parse(temp_path)
        event = corpus.conversations[0].events[0]

        # Extra fields should be in metadata
        assert event.metadata["model"] == "gpt-4"
        assert event.metadata["temperature"] == 0.7
        assert event.metadata["custom_field"] == "custom_value"

    finally:
        temp_path.unlink()


# ============================================================================
# Parser Registry Tests
# ============================================================================


def test_get_default_registry():
    """Test default registry includes all parsers."""
    registry = get_default_registry()

    # Should have all 4 parsers
    assert len(registry._parsers) == 4

    # Check parser types
    parser_types = {type(p).__name__ for p in registry._parsers}
    assert "ChatGPTParser" in parser_types
    assert "ClaudeParser" in parser_types
    assert "CharacterAIParser" in parser_types
    assert "GenericParser" in parser_types


def test_registry_auto_detect_claude():
    """Test registry can auto-detect Claude format."""
    registry = get_default_registry()

    with NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        claude_data = {
            "messages": [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi"},
            ]
        }
        json.dump(claude_data, f)
        temp_path = Path(f.name)

    try:
        parser = registry.find_parser(temp_path)
        assert parser is not None
        assert parser.source_name in ["claude", "generic"]  # Could match either

    finally:
        temp_path.unlink()


def test_registry_auto_detect_generic_csv():
    """Test registry can auto-detect generic CSV."""
    registry = get_default_registry()

    with NamedTemporaryFile(mode="w", suffix=".csv", delete=False, newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["role", "content"])
        writer.writeheader()
        writer.writerow({"role": "user", "content": "test"})
        temp_path = Path(f.name)

    try:
        parser = registry.find_parser(temp_path)
        assert parser is not None
        assert parser.source_name == "generic"

    finally:
        temp_path.unlink()


def test_registry_parse_auto():
    """Test registry can auto-parse a file."""
    registry = get_default_registry()

    with NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
        ]
        json.dump(messages, f)
        temp_path = Path(f.name)

    try:
        corpus = registry.parse_auto(temp_path)
        assert isinstance(corpus, Corpus)
        assert len(corpus.conversations) >= 1

    finally:
        temp_path.unlink()


# ============================================================================
# Error Handling Tests
# ============================================================================


def test_parser_file_not_found():
    """Test parsers handle missing files gracefully."""
    parser = GenericParser()
    nonexistent_path = Path("/nonexistent/path/to/file.json")

    with pytest.raises(FileNotFoundError):
        parser.parse(nonexistent_path)


def test_parser_invalid_json():
    """Test parsers handle invalid JSON gracefully."""
    parser = ClaudeParser()

    with NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        f.write("{ invalid json }")
        temp_path = Path(f.name)

    try:
        # can_parse should return False for invalid JSON
        assert not parser.can_parse(temp_path)
    finally:
        temp_path.unlink()


def test_generic_parser_empty_csv():
    """Test generic parser handles empty CSV."""
    parser = GenericParser()

    with NamedTemporaryFile(mode="w", suffix=".csv", delete=False, newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["role", "content"])
        writer.writeheader()
        # No data rows
        temp_path = Path(f.name)

    try:
        corpus = parser.parse(temp_path)
        # Should return empty corpus, not error
        assert len(corpus.conversations) == 0
    finally:
        temp_path.unlink()
