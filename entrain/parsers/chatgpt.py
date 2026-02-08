"""
ChatGPT export format parser.

Parses ChatGPT conversation exports (conversations.json) into Entrain data model.

See ARCHITECTURE.md Section 4.2 for format specification.

References:
    - ChatGPT exports contain conversations.json with nested message trees
    - Each message has author.role, content.parts, create_time, metadata
"""

import json
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any

from entrain.models import Conversation, Corpus, InteractionEvent
from entrain.parsers.base import BaseParser


class ChatGPTParser(BaseParser):
    """
    Parser for ChatGPT JSON export format.

    ChatGPT exports to a ZIP file containing conversations.json.
    Each conversation contains a tree of message nodes with roles
    (user/assistant/system/tool), content parts, timestamps, and metadata.
    """

    @property
    def source_name(self) -> str:
        return "chatgpt"

    def can_parse(self, path: Path) -> bool:
        """
        Check if this is a ChatGPT export file.

        Accepts:
        - ZIP files containing conversations.json
        - Direct conversations.json files
        """
        if not path.exists():
            return False

        if path.suffix == ".zip":
            try:
                with zipfile.ZipFile(path, "r") as zf:
                    return "conversations.json" in zf.namelist()
            except (zipfile.BadZipFile, PermissionError):
                return False

        if path.name == "conversations.json":
            return True

        return False

    def parse(self, path: Path) -> Corpus:
        """
        Parse ChatGPT export into Corpus.

        Args:
            path: Path to ZIP file or conversations.json

        Returns:
            Corpus with parsed conversations

        Raises:
            ValueError: If format is invalid
            FileNotFoundError: If path doesn't exist
        """
        if not path.exists():
            raise FileNotFoundError(f"Export file not found: {path}")

        # Extract JSON content
        if path.suffix == ".zip":
            json_data = self._extract_from_zip(path)
        else:
            with open(path, "r", encoding="utf-8") as f:
                json_data = json.load(f)

        # Parse conversations
        conversations = []
        for conv_data in json_data:
            try:
                conversation = self._parse_conversation(conv_data)
                if conversation and conversation.events:  # Only include non-empty
                    conversations.append(conversation)
            except Exception as e:
                # Log warning but continue parsing other conversations
                conv_id = conv_data.get("id", "unknown")
                print(f"Warning: Failed to parse conversation {conv_id}: {e}")
                continue

        return Corpus(conversations=conversations)

    def _extract_from_zip(self, zip_path: Path) -> Any:
        """Extract and parse conversations.json from ZIP."""
        with zipfile.ZipFile(zip_path, "r") as zf:
            with zf.open("conversations.json") as f:
                return json.load(f)

    def _parse_conversation(self, conv_data: dict) -> Conversation | None:
        """Parse a single conversation from JSON structure."""
        conv_id = conv_data.get("id", "unknown")
        title = conv_data.get("title", "Untitled")
        create_time = conv_data.get("create_time")
        update_time = conv_data.get("update_time")

        # Extract metadata
        metadata = {
            "title": title,
            "create_time": create_time,
            "update_time": update_time,
        }

        # Parse message tree - ChatGPT uses a tree structure with "mapping"
        events = []
        mapping = conv_data.get("mapping", {})

        # Find the conversation root and traverse in chronological order
        message_nodes = self._flatten_message_tree(mapping)

        for msg_node in message_nodes:
            message = msg_node.get("message")
            if not message:
                continue

            # Extract message details
            msg_id = message.get("id", "")
            author = message.get("author", {})
            role = author.get("role")
            create_time_ts = message.get("create_time")
            content = message.get("content", {})
            msg_metadata = message.get("metadata", {})

            # Skip system and tool messages for analysis
            if role not in ("user", "assistant"):
                continue

            # Extract text content from parts
            parts = content.get("parts", [])
            text_content = self._extract_text_from_parts(parts)

            # Skip empty messages
            if not text_content:
                continue

            # Convert timestamp
            timestamp = None
            if create_time_ts:
                try:
                    timestamp = datetime.fromtimestamp(create_time_ts)
                except (ValueError, OSError):
                    timestamp = datetime.now()  # Fallback
            else:
                timestamp = datetime.now()

            # Extract model info
            model_slug = msg_metadata.get("model_slug", "")
            finish_reason = msg_metadata.get("finish_details", {}).get("type", "")

            event = InteractionEvent(
                id=msg_id or f"{conv_id}_{len(events)}",
                conversation_id=conv_id,
                timestamp=timestamp,
                role=role,
                text_content=text_content,
                metadata={
                    "model": model_slug,
                    "finish_reason": finish_reason,
                    "author_name": author.get("name"),
                },
            )
            events.append(event)

        # Sort by timestamp to ensure chronological order
        events.sort(key=lambda e: e.timestamp)

        return Conversation(
            id=conv_id, source=self.source_name, events=events, metadata=metadata
        )

    def _flatten_message_tree(self, mapping: dict) -> list[dict]:
        """
        Flatten ChatGPT's message tree structure into chronological list.

        ChatGPT stores messages in a tree where each node has children.
        We traverse this to extract messages in order.
        """
        messages = []

        # Collect all message nodes
        for node_id, node in mapping.items():
            if node.get("message"):
                messages.append(node)

        # Sort by creation time
        messages.sort(
            key=lambda n: n.get("message", {}).get("create_time", 0) or 0
        )

        return messages

    def _extract_text_from_parts(self, parts: list) -> str:
        """
        Extract text content from ChatGPT message parts.

        Parts can be strings, dicts, or None. We join all text parts.
        """
        text_parts = []

        for part in parts:
            if isinstance(part, str):
                text_parts.append(part)
            elif isinstance(part, dict):
                # Some parts may have special structure (code, images, etc.)
                # For now, just try to get text content
                if "text" in part:
                    text_parts.append(part["text"])
                elif "content" in part:
                    text_parts.append(str(part["content"]))
            elif part is not None:
                text_parts.append(str(part))

        return "\n".join(text_parts).strip()
