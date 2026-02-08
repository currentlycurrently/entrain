"""
Character.AI export format parser.

Parses Character.AI conversation exports into Entrain data model.

Character.AI exports include:
- Bot metadata (name, description, greeting)
- Chat history (all interactions with the character)

Supports exports from:
- Official Character.AI data export
- CAI Tools browser extension
- Third-party export tools

See ARCHITECTURE.md Section 4 for format specification.

References:
    - Character.AI official export via Profile Settings
    - CAI Tools browser extension exports
    - JSON format contains character info and message history
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from entrain.models import Conversation, Corpus, InteractionEvent
from entrain.parsers.base import BaseParser


class CharacterAIParser(BaseParser):
    """
    Parser for Character.AI conversation export formats.

    Supports multiple Character.AI export formats:
    - Official Character.AI JSON export
    - CAI Tools browser extension format
    - Third-party export tool formats

    The parser attempts to auto-detect the specific format variant.
    """

    @property
    def source_name(self) -> str:
        return "characterai"

    def can_parse(self, path: Path) -> bool:
        """
        Check if this is a Character.AI export file.

        Accepts:
        - JSON files with Character.AI structure
        - Files with character metadata and chat history
        """
        if not path.exists():
            return False

        if path.suffix != ".json":
            return False

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return self._is_characterai_format(data)
        except (json.JSONDecodeError, UnicodeDecodeError, PermissionError):
            return False

    def _is_characterai_format(self, data: Any) -> bool:
        """
        Heuristically detect if JSON data is a Character.AI export.

        Looks for Character.AI-specific patterns:
        - 'character' or 'bot' metadata fields
        - 'histories' or 'chats' array
        - Character.AI-specific field names
        """
        if isinstance(data, dict):
            # Check for Character.AI-specific fields
            characterai_fields = [
                "character",
                "char",
                "bot",
                "character_name",
                "bot_name",
                "greeting",
                "histories",
                "chats",
                "participants",
            ]

            if any(field in data for field in characterai_fields):
                return True

            # Check for Character.AI chat structure
            if "messages" in data and "character" in str(data).lower():
                return True

            # Check for participant structure (Character.AI uses this)
            if "participants" in data:
                participants = data.get("participants", [])
                if isinstance(participants, list):
                    for p in participants:
                        if isinstance(p, dict) and (
                            "is_human" in p or "character_id" in p
                        ):
                            return True

        elif isinstance(data, list):
            # Check if it's an array of Character.AI chats
            if len(data) > 0 and isinstance(data[0], dict):
                if any(
                    field in data[0]
                    for field in ["character", "bot", "histories", "character_name"]
                ):
                    return True

        return False

    def parse(self, path: Path) -> Corpus:
        """
        Parse Character.AI export into Corpus.

        Args:
            path: Path to JSON file

        Returns:
            Corpus with parsed conversations

        Raises:
            ValueError: If format is invalid or not recognized
            FileNotFoundError: If path doesn't exist
        """
        if not path.exists():
            raise FileNotFoundError(f"Export file not found: {path}")

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        conversations = self._parse_json_data(data)

        if not conversations:
            raise ValueError(
                "No valid conversations found in Character.AI export. "
                "The file may be empty or in an unsupported format."
            )

        return Corpus(conversations=conversations)

    def _parse_json_data(self, data: Any) -> list[Conversation]:
        """
        Parse JSON data into conversations.

        Handles multiple format variations:
        - Single character with histories/chats
        - Array of character chats
        - Simple conversation format
        """
        conversations = []

        if isinstance(data, dict):
            # Extract character metadata
            character_name = (
                data.get("character_name")
                or data.get("char_name")
                or data.get("name")
                or data.get("character", {}).get("name")
                or "Unknown Character"
            )

            character_description = (
                data.get("description")
                or data.get("char_description")
                or data.get("character", {}).get("description")
                or ""
            )

            character_greeting = (
                data.get("greeting")
                or data.get("first_mes")
                or data.get("character", {}).get("greeting")
                or ""
            )

            # Look for chat histories
            histories = (
                data.get("histories")
                or data.get("chats")
                or data.get("conversations")
                or []
            )

            if histories and isinstance(histories, list):
                # Multiple chat histories with this character
                for idx, history in enumerate(histories):
                    conv = self._parse_history(
                        history,
                        f"char_{character_name}_{idx}",
                        character_name,
                        character_description,
                        character_greeting,
                    )
                    if conv and conv.events:
                        conversations.append(conv)

            elif "messages" in data or "msgs" in data:
                # Single conversation format
                conv = self._parse_single_conversation(
                    data, character_name, character_description, character_greeting
                )
                if conv and conv.events:
                    conversations.append(conv)

        elif isinstance(data, list):
            # Array of character chats or messages
            if len(data) > 0 and isinstance(data[0], dict):
                if "character" in data[0] or "character_name" in data[0]:
                    # Array of character conversations
                    for idx, item in enumerate(data):
                        char_name = (
                            item.get("character_name")
                            or item.get("name")
                            or f"Character_{idx}"
                        )
                        conv = self._parse_single_conversation(
                            item,
                            char_name,
                            item.get("description", ""),
                            item.get("greeting", ""),
                        )
                        if conv and conv.events:
                            conversations.append(conv)
                else:
                    # Simple message array
                    conv = self._parse_message_array(data, "conversation_0")
                    if conv and conv.events:
                        conversations.append(conv)

        return conversations

    def _parse_history(
        self,
        history: dict | list,
        conv_id: str,
        character_name: str,
        character_description: str,
        character_greeting: str,
    ) -> Conversation | None:
        """Parse a single chat history into a Conversation."""
        if isinstance(history, dict):
            messages = history.get("messages") or history.get("msgs") or []
            history_id = history.get("id") or history.get("history_id") or conv_id
        elif isinstance(history, list):
            messages = history
            history_id = conv_id
        else:
            return None

        events = self._parse_messages(messages, str(history_id), character_name)

        if not events:
            return None

        metadata = {
            "character_name": character_name,
            "character_description": character_description,
            "character_greeting": character_greeting,
        }

        return Conversation(
            id=str(history_id),
            source=self.source_name,
            events=events,
            metadata=metadata,
        )

    def _parse_single_conversation(
        self,
        conv_data: dict,
        character_name: str,
        character_description: str,
        character_greeting: str,
    ) -> Conversation | None:
        """Parse a single conversation object."""
        conv_id = (
            conv_data.get("id")
            or conv_data.get("conversation_id")
            or f"char_{character_name}_0"
        )

        messages = conv_data.get("messages") or conv_data.get("msgs") or []

        events = self._parse_messages(messages, str(conv_id), character_name)

        if not events:
            return None

        metadata = {
            "character_name": character_name,
            "character_description": character_description,
            "character_greeting": character_greeting,
        }

        return Conversation(
            id=str(conv_id),
            source=self.source_name,
            events=events,
            metadata=metadata,
        )

    def _parse_message_array(
        self, messages: list[dict], conv_id: str
    ) -> Conversation | None:
        """Parse a simple message array into a Conversation."""
        events = self._parse_messages(messages, conv_id, "Character")

        if not events:
            return None

        return Conversation(
            id=conv_id,
            source=self.source_name,
            events=events,
            metadata={"character_name": "Character"},
        )

    def _parse_messages(
        self, messages: list, conv_id: str, character_name: str
    ) -> list[InteractionEvent]:
        """
        Parse message array into InteractionEvent list.

        Handles various Character.AI message format variations:
        - is_human field to distinguish user/bot
        - src field with 'human'/'character' values
        - name/author field matching character name
        """
        events = []

        for idx, msg in enumerate(messages):
            if not isinstance(msg, dict):
                continue

            # Determine role (user vs character/assistant)
            role = "assistant"  # Default to character

            # Method 1: Check is_human field
            if "is_human" in msg:
                role = "user" if msg["is_human"] else "assistant"

            # Method 2: Check src field
            elif "src" in msg:
                src = str(msg["src"]).lower()
                if src in ("human", "user"):
                    role = "user"
                elif src in ("character", "bot", "ai"):
                    role = "assistant"

            # Method 3: Check name/author field
            elif "name" in msg or "author" in msg:
                name = str(msg.get("name") or msg.get("author")).lower()
                if name in ("user", "human", "you"):
                    role = "user"
                elif name == character_name.lower() or name in ("character", "bot"):
                    role = "assistant"

            # Method 4: Check swipes or candidate_id (Character.AI specific)
            # If message has swipes/candidates, it's usually from the character
            elif "swipes" in msg or "candidate_id" in msg:
                role = "assistant"

            # Extract content
            content = msg.get("text") or msg.get("content") or msg.get("message") or ""

            # Handle swipes (Character.AI allows regenerating responses)
            # Use the first/selected swipe if available
            if "swipes" in msg and isinstance(msg["swipes"], list):
                swipes = msg["swipes"]
                if swipes:
                    # Use the selected swipe or the first one
                    selected_idx = msg.get("swipe_id", 0)
                    if 0 <= selected_idx < len(swipes):
                        content = swipes[selected_idx]
                    else:
                        content = swipes[0]

            if not isinstance(content, str):
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
                or msg.get("send_date")
                or msg.get("time")
            )

            if timestamp_field:
                timestamp = self._parse_timestamp(timestamp_field)
            else:
                timestamp = datetime.now()

            # Extract message ID
            msg_id = (
                msg.get("id")
                or msg.get("message_id")
                or msg.get("uuid")
                or f"{conv_id}_{idx}"
            )

            # Extract metadata
            msg_metadata = {"character_name": character_name}

            if "swipes" in msg:
                msg_metadata["swipe_count"] = len(msg["swipes"])
                msg_metadata["selected_swipe"] = msg.get("swipe_id", 0)

            if "candidate_id" in msg:
                msg_metadata["candidate_id"] = msg["candidate_id"]

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
        - Unix timestamps (int or float, possibly in milliseconds)
        - ISO 8601 strings
        - Other datetime strings
        """
        if isinstance(timestamp_field, (int, float)):
            # Unix timestamp - might be in seconds or milliseconds
            try:
                # If timestamp is > 1e12, it's likely in milliseconds
                if timestamp_field > 1e12:
                    timestamp_field = timestamp_field / 1000
                return datetime.fromtimestamp(timestamp_field)
            except (ValueError, OSError):
                return datetime.now()

        elif isinstance(timestamp_field, str):
            # Try ISO 8601 format
            try:
                if timestamp_field.endswith("Z"):
                    timestamp_field = timestamp_field[:-1] + "+00:00"
                return datetime.fromisoformat(timestamp_field.replace("Z", "+00:00"))
            except ValueError:
                # Try other common formats
                for fmt in [
                    "%Y-%m-%d %H:%M:%S",
                    "%Y-%m-%dT%H:%M:%S",
                    "%Y/%m/%d %H:%M:%S",
                    "%d/%m/%Y %H:%M:%S",
                ]:
                    try:
                        return datetime.strptime(timestamp_field, fmt)
                    except ValueError:
                        continue

        # Fallback to current time
        return datetime.now()
