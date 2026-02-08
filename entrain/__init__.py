"""
Entrain: A unified framework for measuring AI cognitive influence on humans.

The Entrain Reference Library implements the measurement methodologies described
in the Entrain Framework (FRAMEWORK.md). It provides composable analysis primitives
for researchers and tool builders to measure AI cognitive influence dimensions.

Usage:
    >>> from entrain import Conversation, InteractionEvent
    >>> from entrain.parsers import ChatGPTParser
    >>> from entrain.dimensions import SRAnalyzer

    >>> parser = ChatGPTParser()
    >>> corpus = parser.parse("conversations.json")
    >>> analyzer = SRAnalyzer()
    >>> report = analyzer.analyze_conversation(corpus.conversations[0])

See ARCHITECTURE.md for complete specification.
"""

from entrain.models import (
    ENTRAIN_VERSION,
    AudioFeatures,
    Conversation,
    Corpus,
    DimensionReport,
    EntrainReport,
    IndicatorResult,
    InteractionEvent,
)

__version__ = ENTRAIN_VERSION
__all__ = [
    "ENTRAIN_VERSION",
    "AudioFeatures",
    "Conversation",
    "Corpus",
    "DimensionReport",
    "EntrainReport",
    "IndicatorResult",
    "InteractionEvent",
]
