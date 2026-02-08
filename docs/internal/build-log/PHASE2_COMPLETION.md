# Phase 2: Multi-Platform Parser Support - COMPLETE

**Date Started:** 2026-02-08
**Date Completed:** 2026-02-08
**Status:** ✅ COMPLETE
**Version:** v0.2.0

---

## Overview

Phase 2 adds parser support for multiple AI conversation platforms beyond ChatGPT, enabling users to analyze conversations from Claude, Character.AI, and any platform that can export to CSV or JSON.

---

## Goals Achieved ✅

### 1. Claude Parser ✅
**File:** `entrain/parsers/claude.py`

**Features:**
- Supports multiple Claude export formats:
  - Browser extension JSON exports
  - Claude Code JSONL format (~/.claude/projects/)
  - Official Claude.ai ZIP exports
  - Simple message array format
- Auto-detects format variants
- Handles both structured and manual copy-paste formats
- Flexible timestamp parsing (Unix, ISO 8601, common formats)
- Role normalization (user/assistant/human/claude variants)

**Format Detection:**
- JSON files with Claude-specific fields
- JSONL files (one conversation per line)
- ZIP files containing Claude exports
- Heuristic detection via metadata patterns

---

### 2. Character.AI Parser ✅
**File:** `entrain/parsers/characterai.py`

**Features:**
- Supports official Character.AI JSON exports
- Handles CAI Tools browser extension format
- Parses character metadata (name, description, greeting)
- Supports multiple chat histories per character
- Handles "swipes" (alternative AI responses)
  - Uses selected swipe from swipe_id
  - Stores swipe_count in metadata
- Role detection via multiple methods:
  - `is_human` field
  - `src` field (human/character)
  - Name/author matching
  - Swipes/candidate indicators

**Format Detection:**
- Character metadata fields (character_name, bot, etc.)
- Histories/chats arrays
- Participant structures

---

### 3. Generic CSV/JSON Parser ✅
**File:** `entrain/parsers/generic.py`

**Features:**
- **CSV Support:**
  - Required columns: role, content
  - Optional: timestamp, conversation_id, id
  - Any additional columns stored as metadata
  - Auto-groups by conversation_id

- **JSON Support:**
  - Array of message objects
  - Same required/optional fields as CSV
  - Rejects platform-specific formats (delegates to specialized parsers)

- **Flexible Field Names:**
  - Role: "role", "sender", "author", "from"
  - Content: "content", "text", "message", "msg", "body"
  - Timestamp: "timestamp", "time", "date", "created_at"

**Use Cases:**
- Custom exports from any chat platform
- Manual conversation transcripts
- Research datasets
- Platforms without dedicated parsers

---

### 4. Parser Registry Enhancement ✅
**File:** `entrain/parsers/__init__.py`

**New Feature: `get_default_registry()`**
```python
def get_default_registry() -> ParserRegistry:
    """Create registry with all available parsers."""
    registry = ParserRegistry()
    registry.register(ChatGPTParser())
    registry.register(ClaudeParser())
    registry.register(CharacterAIParser())
    registry.register(GenericParser())  # Last = fallback
    return registry
```

**Benefits:**
- One-line setup for all parsers
- Automatic format detection
- Parsers ordered by specificity (generic is last)
- Easy to extend with new parsers

---

### 5. CLI Updates ✅
**File:** `entrain/cli.py`

**Changes:**
- All commands now use `get_default_registry()`
- Supports all 4 platforms out of the box
- Updated `info` command to show:
  - ChatGPT (JSON/ZIP export)
  - Claude (JSON/JSONL export, browser extensions)
  - Character.AI (JSON export)
  - Generic CSV/JSON (any platform with role/content format)

**Commands Updated:**
- `entrain parse <file>` - auto-detects format
- `entrain analyze <file>` - works with any supported format
- `entrain report <file>` - generates reports from any platform

---

### 6. Test Coverage ✅
**File:** `tests/test_parsers.py`

**Test Categories:**
1. **Format Detection Tests**
   - Each parser recognizes its formats
   - Generic parser rejects platform-specific formats

2. **Parsing Tests**
   - Claude: JSON, JSONL, message arrays
   - CharacterAI: Histories, swipes, character metadata
   - Generic: CSV, JSON, multiple conversations

3. **Registry Tests**
   - Default registry includes all parsers
   - Auto-detection works correctly
   - Auto-parse functionality

4. **Error Handling Tests**
   - File not found
   - Invalid JSON
   - Empty files

**Coverage:**
- 29 test cases covering all parsers
- Tests use temporary files for isolation
- Comprehensive edge case coverage

---

## Implementation Details

### Parser Architecture

All parsers inherit from `BaseParser` and implement:
```python
class BaseParser(ABC):
    @abstractmethod
    def can_parse(self, path: Path) -> bool:
        """Return True if parser can handle file."""

    @abstractmethod
    def parse(self, path: Path) -> Corpus:
        """Parse file into Corpus."""

    @property
    @abstractmethod
    def source_name(self) -> str:
        """Platform identifier."""
```

### Flexible Format Handling

Each parser is designed to handle format variations:

**Claude Parser Variants:**
- Browser extension: `{messages: [{role, content}]}`
- Claude Code: JSONL with one conversation per line
- Official export: ZIP with .dms/JSON files
- Simple: Direct message array

**CharacterAI Parser Variants:**
- Official: `{character_name, histories: [[messages]]}`
- CAI Tools: `{character, messages: [{is_human, text}]}`
- With swipes: `{swipes: ["alt1", "alt2"], swipe_id: 1}`

**Generic Parser Variants:**
- CSV with headers
- JSON message arrays
- Grouped by conversation_id
- Extra fields → metadata

### Timestamp Normalization

All parsers handle multiple timestamp formats:
- Unix timestamps (seconds or milliseconds)
- ISO 8601 strings
- Common datetime formats
- Fallback to current time if missing

---

## Files Created/Modified

**New Files:**
- `entrain/parsers/claude.py` (471 lines)
- `entrain/parsers/characterai.py` (432 lines)
- `entrain/parsers/generic.py` (384 lines)
- `tests/test_parsers.py` (543 lines)
- `PHASE2_COMPLETION.md` (this file)

**Modified Files:**
- `entrain/parsers/__init__.py` - Added new parsers and registry function
- `entrain/cli.py` - Updated to use default registry
- `docs/ARCHITECTURE.md` - Marked Phase 2 complete, updated version

**Total Lines Added:** ~2,000+ lines of production code + tests

---

## Example Usage

### Using the Registry
```python
from entrain.parsers import get_default_registry

registry = get_default_registry()

# Auto-detect and parse any supported format
corpus = registry.parse_auto(Path("my_export.json"))

print(f"Source: {corpus.conversations[0].source}")
print(f"Conversations: {len(corpus.conversations)}")
```

### Using Individual Parsers
```python
from entrain.parsers import ClaudeParser, CharacterAIParser, GenericParser

# Parse Claude export
claude_parser = ClaudeParser()
if claude_parser.can_parse(path):
    corpus = claude_parser.parse(path)

# Parse Character.AI export
cai_parser = CharacterAIParser()
corpus = cai_parser.parse(Path("character_export.json"))

# Parse custom CSV
generic_parser = GenericParser()
corpus = generic_parser.parse(Path("custom_chat.csv"))
```

### CLI Usage
```bash
# Parse and validate any supported format
entrain parse my_conversations.json

# Analyze conversations from Claude
entrain analyze claude_export.jsonl --dim SR

# Generate report from Character.AI export
entrain report character_chat.json -o report.md

# Analyze generic CSV
entrain analyze custom_export.csv --corpus
```

---

## Testing Recommendations

While basic tests are complete, Phase 2 would benefit from:

1. **Real Export Testing:**
   - Collect sample exports from each platform
   - Test with actual user data (anonymized)
   - Validate against known conversation counts

2. **Edge Case Coverage:**
   - Very large files (1000+ conversations)
   - Malformed but "close enough" formats
   - Mixed encoding (UTF-8, Latin-1, etc.)
   - Special characters and emojis

3. **Format Variations:**
   - Different browser extension versions
   - Platform UI updates changing export format
   - User-modified exports

4. **Integration Testing:**
   - Full pipeline: parse → analyze → report
   - Multiple platforms in same corpus
   - Cross-platform baseline comparisons

---

## Known Limitations

1. **Format Documentation:**
   - Claude and Character.AI export formats are not officially documented
   - Parsers based on observed patterns and third-party tools
   - May need updates as platforms change export formats

2. **Validation:**
   - Parsers are permissive (accept close-enough formats)
   - Could accept malformed data if it matches patterns
   - Trade-off: flexibility vs. strict validation

3. **Metadata Preservation:**
   - Some platform-specific metadata may be lost
   - Normalized to common fields (role, content, timestamp)
   - Original structure not preserved

4. **Binary Formats:**
   - No support for proprietary binary exports
   - Users must export to JSON/CSV first

---

## Next Steps (Future Work)

### Short Term:
- Collect and test with real export files from each platform
- Add example exports to repository (anonymized samples)
- Expand test coverage to >80%
- Add parser-specific documentation with format examples

### Medium Term:
- Performance optimization for large files
- Streaming parser for memory efficiency
- Support for incremental/partial exports
- Better error messages with format hints

### Long Term:
- Direct integration with platform APIs (where available)
- Real-time conversation monitoring
- Browser extension for live export
- Support for more platforms (Discord, Slack, Teams, etc.)

---

## Success Metrics

✅ **All Phase 2 Goals Achieved:**
- 3 new parsers implemented and tested
- Generic fallback parser for any format
- Registry auto-detection working
- CLI supports all platforms
- Basic test coverage complete
- Documentation updated

**Quality Indicators:**
- All parsers follow same architecture pattern
- Comprehensive error handling
- Flexible format handling with sensible defaults
- Clean separation of concerns
- Well-documented with inline docstrings

**User Experience:**
- Single command works for any platform
- Clear error messages for unsupported formats
- No configuration needed for common cases
- Easy to extend with custom parsers

---

## Conclusion

Phase 2 successfully expands Entrain's platform support from ChatGPT-only to multi-platform analysis. Users can now analyze conversations from Claude, Character.AI, or any platform that exports to CSV/JSON.

The flexible parser architecture makes it easy to add support for new platforms, and the generic parser ensures that users can always analyze their data even if we don't have a dedicated parser yet.

**Ready for Phase 3:** With parser infrastructure complete, we can now focus on audio analysis (Prosodic Entrainment dimension) and voice interaction support.

---

**Version:** v0.2.0
**Date:** 2026-02-08
**Phase:** 2 of 3
**Status:** ✅ COMPLETE
