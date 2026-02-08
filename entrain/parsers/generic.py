"""
Generic CSV/JSON parser for custom conversation exports.

Provides a simple way to analyze conversations from any platform
where users can manually structure their exports.

CSV format requirements:
- Required columns: role, content
- Optional columns: timestamp, conversation_id, id, metadata columns

JSON format requirements:
- Array of message objects with at least: role, content
- Optional fields: timestamp, conversation_id, id, and any metadata

See ARCHITECTURE.md Section 4.4 for format specification.

Example CSV:
    timestamp,role,content,conversation_id
    2025-01-01 10:00:00,user,Hello!,conv1
    2025-01-01 10:00:05,assistant,Hi there!,conv1

Example JSON:
    [
      {"role": "user", "content": "Hello!", "timestamp": "2025-01-01 10:00:00"},
      {"role": "assistant", "content": "Hi there!", "timestamp": "2025-01-01 10:00:05"}
    ]
"""

from __future__ import annotations

import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from entrain.models import Conversation, Corpus, InteractionEvent
from entrain.parsers.base import BaseParser


class GenericParser(BaseParser):
    """
    Parser for generic CSV and JSON conversation exports.

    Accepts simple, user-structured conversation data where each row/object
    represents a single message with at minimum a role and content.

    This parser is useful for:
    - Custom exports from any chat platform
    - Manual conversation transcripts
    - Data from platforms without dedicated parsers
    - Research datasets

    Required fields:
    - role: 'user' or 'assistant' (or similar variants)
    - content: Message text

    Optional fields:
    - timestamp: When the message was sent
    - conversation_id: Group messages into separate conversations
    - id: Unique message identifier
    - Any other fields are stored as metadata
    """

    @property
    def source_name(self) -> str:
        return "generic"

    def can_parse(self, path: Path) -> bool:
        """
        Check if this is a generic CSV or JSON file.

        This parser is intentionally permissive - it will attempt to parse
        any CSV or JSON file. It should be registered last in the parser
        registry as a fallback.
        """
        if not path.exists():
            return False

        # Accept CSV files
        if path.suffix == ".csv":
            return self._validate_csv(path)

        # Accept JSON files (but only if they look like message arrays)
        if path.suffix == ".json":
            return self._validate_json(path)

        return False

    def _validate_csv(self, path: Path) -> bool:
        """Validate that CSV has required columns (role, content)."""
        try:
            with open(path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                headers = reader.fieldnames or []

                # Must have at least role and content columns
                # Accept variations in column names
                has_role = any(
                    h.lower() in ("role", "sender", "author", "from") for h in headers
                )
                has_content = any(
                    h.lower() in ("content", "text", "message", "msg", "body")
                    for h in headers
                )

                return has_role and has_content
        except (csv.Error, UnicodeDecodeError, PermissionError):
            return False

    def _validate_json(self, path: Path) -> bool:
        """
        Validate that JSON is an array of message objects.

        Only returns True for simple message arrays to avoid conflicting
        with more specific parsers (Claude, CharacterAI, ChatGPT).
        """
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

                # Must be an array
                if not isinstance(data, list):
                    return False

                # Must have at least one message
                if len(data) == 0:
                    return True  # Empty is valid but will produce empty corpus

                # Check first item has basic message structure
                first_item = data[0]
                if not isinstance(first_item, dict):
                    return False

                # Must have role-like and content-like fields
                role_fields = {"role", "sender", "author", "from"}
                content_fields = {"content", "text", "message", "msg", "body"}

                has_role = any(k.lower() in role_fields for k in first_item.keys())
                has_content = any(k.lower() in content_fields for k in first_item.keys())

                if not (has_role and has_content):
                    return False

                # Reject if it looks like a platform-specific format
                # (those should be handled by dedicated parsers)
                platform_specific_fields = {
                    "mapping",  # ChatGPT
                    "character",
                    "character_name",  # CharacterAI
                    "histories",  # CharacterAI
                    "swipes",  # CharacterAI
                }

                if any(field in first_item for field in platform_specific_fields):
                    return False

                return True

        except (json.JSONDecodeError, UnicodeDecodeError, PermissionError):
            return False

    def parse(self, path: Path) -> Corpus:
        """
        Parse generic CSV or JSON export into Corpus.

        Args:
            path: Path to CSV or JSON file

        Returns:
            Corpus with parsed conversations

        Raises:
            ValueError: If format is invalid
            FileNotFoundError: If path doesn't exist
        """
        if not path.exists():
            raise FileNotFoundError(f"Export file not found: {path}")

        if path.suffix == ".csv":
            return self._parse_csv(path)
        elif path.suffix == ".json":
            return self._parse_json(path)
        else:
            raise ValueError(f"Unsupported file type: {path.suffix}")

    def _parse_csv(self, csv_path: Path) -> Corpus:
        """Parse CSV file into Corpus."""
        conversations_dict: dict[str, list[dict]] = {}

        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            for row_num, row in enumerate(reader, 1):
                # Get conversation ID (default to single conversation)
                conv_id = (
                    row.get("conversation_id")
                    or row.get("conv_id")
                    or row.get("chat_id")
                    or "conversation_0"
                )

                # Add to appropriate conversation
                if conv_id not in conversations_dict:
                    conversations_dict[conv_id] = []

                conversations_dict[conv_id].append(row)

        # Convert to Conversation objects
        conversations = []
        for conv_id, messages in conversations_dict.items():
            conv = self._parse_message_rows(messages, conv_id)
            if conv and conv.events:
                conversations.append(conv)

        return Corpus(conversations=conversations)

    def _parse_json(self, json_path: Path) -> Corpus:
        """Parse JSON file into Corpus."""
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, list):
            raise ValueError("JSON must be an array of message objects")

        # Group by conversation_id if present
        conversations_dict: dict[str, list[dict]] = {}

        for msg in data:
            if not isinstance(msg, dict):
                continue

            conv_id = (
                msg.get("conversation_id")
                or msg.get("conv_id")
                or msg.get("chat_id")
                or "conversation_0"
            )

            if conv_id not in conversations_dict:
                conversations_dict[conv_id] = []

            conversations_dict[conv_id].append(msg)

        # Convert to Conversation objects
        conversations = []
        for conv_id, messages in conversations_dict.items():
            conv = self._parse_message_rows(messages, str(conv_id))
            if conv and conv.events:
                conversations.append(conv)

        return Corpus(conversations=conversations)

    def _parse_message_rows(
        self, messages: list[dict], conv_id: str
    ) -> Conversation | None:
        """Parse message rows/objects into a Conversation."""
        events = []

        for idx, msg in enumerate(messages):
            # Extract role
            role = (
                msg.get("role")
                or msg.get("sender")
                or msg.get("author")
                or msg.get("from")
                or ""
            )

            # Normalize role
            role_lower = str(role).lower()
            if role_lower in ("user", "human", "you"):
                role = "user"
            elif role_lower in ("assistant", "ai", "bot", "system"):
                role = "assistant"
            else:
                # Unknown role, skip
                continue

            # Extract content
            content = (
                msg.get("content")
                or msg.get("text")
                or msg.get("message")
                or msg.get("msg")
                or msg.get("body")
                or ""
            )

            if not isinstance(content, str):
                content = str(content)

            content = content.strip()

            # Skip empty messages
            if not content:
                continue

            # Extract timestamp
            timestamp_field = (
                msg.get("timestamp")
                or msg.get("time")
                or msg.get("date")
                or msg.get("created_at")
            )

            if timestamp_field:
                timestamp = self._parse_timestamp(timestamp_field)
            else:
                # No timestamp - use current time with small offset per message
                # This maintains chronological order
                timestamp = datetime.now()

            # Extract message ID
            msg_id = msg.get("id") or msg.get("message_id") or f"{conv_id}_{idx}"

            # Extract any additional fields as metadata
            metadata = {}
            known_fields = {
                "role",
                "sender",
                "author",
                "from",
                "content",
                "text",
                "message",
                "msg",
                "body",
                "timestamp",
                "time",
                "date",
                "created_at",
                "id",
                "message_id",
                "conversation_id",
                "conv_id",
                "chat_id",
            }

            for key, value in msg.items():
                if key not in known_fields and value:
                    # Store additional fields as metadata
                    metadata[key] = value

            event = InteractionEvent(
                id=str(msg_id),
                conversation_id=conv_id,
                timestamp=timestamp,
                role=role,
                text_content=content,
                metadata=metadata,
            )
            events.append(event)

        # Sort by timestamp to ensure chronological order
        events.sort(key=lambda e: e.timestamp)

        if not events:
            return None

        # Create conversation metadata from first message if available
        conversation_metadata = {"title": f"Conversation {conv_id}"}

        return Conversation(
            id=conv_id,
            source=self.source_name,
            events=events,
            metadata=conversation_metadata,
        )

    def _parse_timestamp(self, timestamp_field: Any) -> datetime:
        """
        Parse various timestamp formats into datetime.

        Handles:
        - Unix timestamps (int or float)
        - ISO 8601 strings
        - Common datetime string formats
        """
        if isinstance(timestamp_field, (int, float)):
            # Unix timestamp
            try:
                # If timestamp is > 1e12, it's likely in milliseconds
                if timestamp_field > 1e12:
                    timestamp_field = timestamp_field / 1000
                return datetime.fromtimestamp(timestamp_field)
            except (ValueError, OSError):
                return datetime.now()

        elif isinstance(timestamp_field, str):
            # Try ISO 8601 format first
            try:
                if timestamp_field.endswith("Z"):
                    timestamp_field = timestamp_field[:-1] + "+00:00"
                return datetime.fromisoformat(timestamp_field.replace("Z", "+00:00"))
            except ValueError:
                pass

            # Try common formats
            formats = [
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%dT%H:%M:%S",
                "%Y/%m/%d %H:%M:%S",
                "%d/%m/%Y %H:%M:%S",
                "%m/%d/%Y %H:%M:%S",
                "%Y-%m-%d",
                "%d/%m/%Y",
                "%m/%d/%Y",
            ]

            for fmt in formats:
                try:
                    return datetime.strptime(timestamp_field, fmt)
                except ValueError:
                    continue

        # Fallback to current time
        return datetime.now()
