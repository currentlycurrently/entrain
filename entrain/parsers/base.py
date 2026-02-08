"""
Abstract base class for chat export parsers.

All parsers implement this interface to normalize different chat platform
export formats into the Entrain data model.

See ARCHITECTURE.md Section 4.1 for specification.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from entrain.models import Corpus


class BaseParser(ABC):
    """
    Abstract base for chat export parsers.

    Each parser knows how to convert a specific platform's export format
    (e.g., ChatGPT's JSON, Claude's export) into Entrain's normalized
    Corpus model.
    """

    @abstractmethod
    def can_parse(self, path: Path) -> bool:
        """
        Return True if this parser can handle the given file.

        Args:
            path: Path to the export file or directory

        Returns:
            True if this parser recognizes the format
        """
        pass

    @abstractmethod
    def parse(self, path: Path) -> Corpus:
        """
        Parse the export file into an Entrain Corpus.

        Args:
            path: Path to the export file or directory

        Returns:
            Corpus containing parsed conversations

        Raises:
            ValueError: If the file format is invalid or unsupported
            FileNotFoundError: If the path does not exist
        """
        pass

    @property
    @abstractmethod
    def source_name(self) -> str:
        """
        The source platform name (e.g., 'chatgpt', 'claude').

        Returns:
            Lowercase platform identifier
        """
        pass


class ParserRegistry:
    """
    Registry for auto-detecting and selecting appropriate parser.

    Usage:
        >>> registry = ParserRegistry()
        >>> registry.register(ChatGPTParser())
        >>> parser = registry.find_parser(Path("conversations.json"))
        >>> corpus = parser.parse(Path("conversations.json"))
    """

    def __init__(self):
        self._parsers: list[BaseParser] = []

    def register(self, parser: BaseParser) -> None:
        """Register a parser instance."""
        self._parsers.append(parser)

    def find_parser(self, path: Path) -> BaseParser | None:
        """
        Find a parser that can handle the given file.

        Args:
            path: Path to the export file

        Returns:
            Parser instance that can handle this file, or None if no match
        """
        for parser in self._parsers:
            if parser.can_parse(path):
                return parser
        return None

    def parse_auto(self, path: Path) -> Corpus:
        """
        Auto-detect format and parse.

        Args:
            path: Path to the export file

        Returns:
            Parsed Corpus

        Raises:
            ValueError: If no parser can handle this format
        """
        parser = self.find_parser(path)
        if parser is None:
            raise ValueError(
                f"No parser found for {path}. "
                f"Supported formats: {', '.join(p.source_name for p in self._parsers)}"
            )
        return parser.parse(path)
