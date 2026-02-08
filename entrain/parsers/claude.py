"""
Claude export format parser.

Parses Claude conversation exports into Entrain data model.
Supports multiple export formats:
- Browser extension JSON exports (array of messages)
- Claude Code JSONL format (~/.claude/projects/)
- Official Claude.ai export (ZIP with JSON)

See ARCHITECTURE.md Section 4.3 for format specification.

References:
    - Claude browser extensions export conversations as JSON
    - Claude Code stores conversations as JSONL in ~/.claude/projects/
    - Official exports provide ZIP with .dms/JSON format
"""

from __future__ import annotations

import json
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any

from entrain.models import Conversation, Corpus, InteractionEvent
from entrain.parsers.base import BaseParser


class ClaudeParser(BaseParser):
    """
    Parser for Claude conversation export formats.

    Supports multiple Claude export formats:
    - JSON files with conversations array
    - JSONL files (one conversation per line)
    - ZIP files containing Claude exports
    - Simple message array format from browser extensions

    The parser attempts to auto-detect the specific format variant.
    """

    @property
    def source_name(self) -> str:
        return "claude"

    def can_parse(self, path: Path) -> bool:
        """
        Check if this is a Claude export file.

        Accepts:
        - JSON files with Claude conversation structure
        - JSONL files (Claude Code format)
        - ZIP files containing Claude exports
        """
        if not path.exists():
            return False

        # Check ZIP files
        if path.suffix == ".zip":
            try:
                with zipfile.ZipFile(path, "r") as zf:
                    # Look for Claude-specific files
                    names = zf.namelist()
                    return any(
                        "claude" in name.lower()
                        or name.endswith(".jsonl")
                        or name.endswith("conversations.json")
                        for name in names
                    )
            except (zipfile.BadZipFile, PermissionError):
                return False

        # Check JSONL files
        if path.suffix == ".jsonl":
            return True

        # Check JSON files
        if path.suffix == ".json":
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # Try to detect Claude format by looking for common fields
                    return self._is_claude_format(data)
            except (json.JSONDecodeError, UnicodeDecodeError, PermissionError):
                return False

        return False

    def _is_claude_format(self, data: Any) -> bool:
        """
        Heuristically detect if JSON data is a Claude export.

        Looks for common Claude-specific patterns:
        - 'claude' in metadata or conversation fields
        - Message structure with 'role' and 'content'
        - Conversation array with Claude-specific fields
        """
        if isinstance(data, dict):
            # Check for Claude-specific metadata
            if any(
                key in data
                for key in [
                    "claude_version",
                    "anthropic",
                    "model",
                    "conversation_id",
                    "uuid",
                ]
            ):
                return True

            # Check if it has messages array with role/content
            if "messages" in data:
                messages = data["messages"]
                if isinstance(messages, list) and len(messages) > 0:
                    first_msg = messages[0]
                    if isinstance(first_msg, dict) and "role" in first_msg:
                        return True

            # Check if it's a conversation object
            if "conversation" in data or "chat" in data:
                return True

        elif isinstance(data, list):
            # Check if it's an array of conversations
            if len(data) > 0 and isinstance(data[0], dict):
                first_item = data[0]
                # Look for message-like structure
                if "role" in first_item and "content" in first_item:
                    return True
                # Look for conversation structure
                if "messages" in first_item or "conversation" in first_item:
                    return True

        return False

    def parse(self, path: Path) -> Corpus:
        """
        Parse Claude export into Corpus.

        Args:
            path: Path to ZIP, JSON, or JSONL file

        Returns:
            Corpus with parsed conversations

        Raises:
            ValueError: If format is invalid or not recognized
            FileNotFoundError: If path doesn't exist
        """
        if not path.exists():
            raise FileNotFoundError(f"Export file not found: {path}")

        # Determine format and parse accordingly
        if path.suffix == ".zip":
            return self._parse_zip(path)
        elif path.suffix == ".jsonl":
            return self._parse_jsonl(path)
        else:  # .json
            return self._parse_json(path)

    def _parse_zip(self, zip_path: Path) -> Corpus:
        """Parse Claude export from ZIP file."""
        conversations = []

        with zipfile.ZipFile(zip_path, "r") as zf:
            for filename in zf.namelist():
                if filename.endswith(".json") or filename.endswith(".jsonl"):
                    try:
                        with zf.open(filename) as f:
                            content = f.read().decode("utf-8")
                            if filename.endswith(".jsonl"):
                                conv = self._parse_jsonl_content(content)
                                conversations.extend(conv)
                            else:
                                data = json.loads(content)
                                conv = self._parse_json_data(data)
                                conversations.extend(conv)
                    except Exception as e:
                        print(f"Warning: Failed to parse {filename}: {e}")
                        continue

        return Corpus(conversations=conversations)

    def _parse_jsonl(self, jsonl_path: Path) -> Corpus:
        """Parse Claude Code JSONL format (one conversation per line)."""
        with open(jsonl_path, "r", encoding="utf-8") as f:
            content = f.read()
        return Corpus(conversations=self._parse_jsonl_content(content))

    def _parse_jsonl_content(self, content: str) -> list[Conversation]:
        """Parse JSONL content into conversations."""
        conversations = []
        for line_num, line in enumerate(content.strip().split("\n"), 1):
            if not line.strip():
                continue
            try:
                data = json.loads(line)
                conv = self._parse_conversation_object(data, f"line_{line_num}")
                if conv and conv.events:
                    conversations.append(conv)
            except json.JSONDecodeError as e:
                print(f"Warning: Invalid JSON on line {line_num}: {e}")
                continue
        return conversations

    def _parse_json(self, json_path: Path) -> Corpus:
        """Parse JSON file containing Claude conversations."""
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return Corpus(conversations=self._parse_json_data(data))

    def _parse_json_data(self, data: Any) -> list[Conversation]:
        """
        Parse JSON data into conversations.

        Handles multiple format variations:
        - Array of conversations
        - Single conversation object
        - Object with 'conversations' key
        - Simple message array
        """
        conversations = []

        if isinstance(data, list):
            # Could be array of conversations or array of messages
            if len(data) > 0 and isinstance(data[0], dict):
                if "messages" in data[0] or "conversation" in data[0]:
                    # Array of conversation objects
                    for idx, conv_data in enumerate(data):
                        conv = self._parse_conversation_object(
                            conv_data, f"conv_{idx}"
                        )
                        if conv and conv.events:
                            conversations.append(conv)
                elif "role" in data[0] and "content" in data[0]:
                    # Simple message array - treat as single conversation
                    conv = self._parse_message_array(data, "conversation_0")
                    if conv and conv.events:
                        conversations.append(conv)

        elif isinstance(data, dict):
            # Single conversation object or container
            if "conversations" in data:
                # Container with conversations array
                for idx, conv_data in enumerate(data["conversations"]):
                    conv = self._parse_conversation_object(conv_data, f"conv_{idx}")
                    if conv and conv.events:
                        conversations.append(conv)
            elif "messages" in data:
                # Single conversation with messages
                conv = self._parse_conversation_object(data, "conversation_0")
                if conv and conv.events:
                    conversations.append(conv)
            else:
                # Try to parse as conversation object
                conv = self._parse_conversation_object(data, "conversation_0")
                if conv and conv.events:
                    conversations.append(conv)

        return conversations

    def _parse_conversation_object(
        self, conv_data: dict, default_id: str
    ) -> Conversation | None:
        """Parse a conversation object into Conversation model."""
        # Extract conversation metadata
        conv_id = conv_data.get("id") or conv_data.get("uuid") or default_id
        title = conv_data.get("title") or conv_data.get("name") or "Untitled"
        created_at = conv_data.get("created_at") or conv_data.get("timestamp")
        updated_at = conv_data.get("updated_at")

        metadata = {
            "title": title,
            "created_at": created_at,
            "updated_at": updated_at,
        }

        # Add model info if available
        if "model" in conv_data:
            metadata["model"] = conv_data["model"]

        # Extract messages
        messages = conv_data.get("messages") or conv_data.get("chat") or []

        # Parse messages into events
        events = self._parse_messages(messages, conv_id)

        if not events:
            return None

        return Conversation(
            id=str(conv_id), source=self.source_name, events=events, metadata=metadata
        )

    def _parse_message_array(
        self, messages: list[dict], conv_id: str
    ) -> Conversation | None:
        """Parse a simple message array into a Conversation."""
        events = self._parse_messages(messages, conv_id)

        if not events:
            return None

        return Conversation(
            id=conv_id,
            source=self.source_name,
            events=events,
            metadata={"title": "Untitled"},
        )

    def _parse_messages(
        self, messages: list[dict], conv_id: str
    ) -> list[InteractionEvent]:
        """
        Parse message array into InteractionEvent list.

        Handles various message format variations:
        - role/content structure
        - sender/text structure
        - Different timestamp formats
        """
        events = []

        for idx, msg in enumerate(messages):
            if not isinstance(msg, dict):
                continue

            # Extract role (user/assistant)
            role = msg.get("role") or msg.get("sender") or msg.get("author")

            # Normalize role to 'user' or 'assistant'
            if role in ("human", "user", "User"):
                role = "user"
            elif role in ("assistant", "claude", "Claude", "ai", "bot"):
                role = "assistant"
            elif role == "system":
                # Skip system messages
                continue
            else:
                # Unknown role, skip
                continue

            # Extract content
            content = msg.get("content") or msg.get("text") or msg.get("message") or ""

            # Handle content as array (some formats have content as array of parts)
            if isinstance(content, list):
                content = "\n".join(
                    str(part.get("text", part) if isinstance(part, dict) else part)
                    for part in content
                )
            elif not isinstance(content, str):
                content = str(content)

            content = content.strip()

            # Skip empty messages
            if not content:
                continue

            # Extract timestamp
            timestamp = None
            timestamp_field = (
                msg.get("timestamp")
                or msg.get("created_at")
                or msg.get("time")
                or msg.get("date")
            )

            if timestamp_field:
                timestamp = self._parse_timestamp(timestamp_field)
            else:
                # Fallback to current time with offset based on message order
                timestamp = datetime.now()

            # Extract message ID
            msg_id = msg.get("id") or msg.get("uuid") or f"{conv_id}_{idx}"

            # Extract metadata
            msg_metadata = {}
            if "model" in msg:
                msg_metadata["model"] = msg["model"]
            if "attachments" in msg:
                msg_metadata["has_attachments"] = True

            event = InteractionEvent(
                id=str(msg_id),
                conversation_id=conv_id,
                timestamp=timestamp,
                role=role,
                text_content=content,
                metadata=msg_metadata,
            )
            events.append(event)

        # Sort by timestamp to ensure chronological order
        events.sort(key=lambda e: e.timestamp)

        return events

    def _parse_timestamp(self, timestamp_field: Any) -> datetime:
        """
        Parse various timestamp formats into datetime.

        Handles:
        - Unix timestamps (int or float)
        - ISO 8601 strings
        - Other datetime strings
        """
        if isinstance(timestamp_field, (int, float)):
            # Unix timestamp
            try:
                return datetime.fromtimestamp(timestamp_field)
            except (ValueError, OSError):
                return datetime.now()

        elif isinstance(timestamp_field, str):
            # Try ISO 8601 format
            try:
                # Handle ISO format with 'Z' timezone
                if timestamp_field.endswith("Z"):
                    timestamp_field = timestamp_field[:-1] + "+00:00"
                return datetime.fromisoformat(timestamp_field.replace("Z", "+00:00"))
            except ValueError:
                # Try other common formats
                for fmt in [
                    "%Y-%m-%d %H:%M:%S",
                    "%Y-%m-%dT%H:%M:%S",
                    "%Y/%m/%d %H:%M:%S",
                ]:
                    try:
                        return datetime.strptime(timestamp_field, fmt)
                    except ValueError:
                        continue

        # Fallback to current time
        return datetime.now()
