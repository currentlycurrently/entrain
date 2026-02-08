# Feature Extractor Tests

This directory contains comprehensive tests for Entrain's feature extraction modules.

## Test Files

### `test_text_features.py` (683 lines, 58 tests)
Tests for `entrain/features/text.py` - **100% coverage** ✨

**Test Categories:**
- Initialization & Pattern Loading (3 tests)
- Vocabulary Extraction (4 tests)
- Sentence Lengths (4 tests)
- Type-Token Ratio (4 tests)
- Hedging Patterns (5 tests)
- Validation Language (4 tests)
- Attribution Language (5 tests)
- Question Type Classification (6 tests)
- Turn Intent Classification (6 tests)
- Sentiment Extraction (5 tests)
- Emotional Content Ratio (6 tests)
- Structural Formatting (6 tests)

**Key Features Tested:**
- JSON pattern file loading (attribution, hedging, validation)
- Case-insensitive pattern matching
- Context extraction (30-char windows)
- Edge cases (empty text, None values)
- Intent classification for decision delegation detection
- Emotional vs functional content ratios

### `test_temporal_features.py` (667 lines, 43 tests)
Tests for `entrain/features/temporal.py` - **99% coverage**

**Test Categories:**
- Helper Classes (3 tests) - TimeSeries, Distribution, Trajectory
- Interaction Frequency (6 tests) - Daily, weekly, monthly windows
- Session Duration Trend (4 tests)
- Time of Day Distribution (5 tests) - 4 time bins
- Indicator Trajectory (7 tests) - Trend detection & slope calculation
- Emotional vs Functional Trajectory (5 tests)
- Edge Cases (13 tests spread across categories)

**Key Features Tested:**
- Linear regression for trend analysis
- Time window aggregation (day/week/month)
- Time-of-day binning (night/morning/afternoon/evening)
- Trajectory trend detection (increasing/decreasing/stable)
- Graceful handling of insufficient data
- User event filtering

### `test_audio.py` (pre-existing)
Tests for audio feature extraction (prosodic entrainment analysis).

## Test Patterns & Best Practices

### 1. Fixture Usage

```python
@pytest.fixture
def text_extractor():
    """Create a TextFeatureExtractor instance."""
    return TextFeatureExtractor()

@pytest.fixture
def sample_timestamp():
    """Base timestamp for test data."""
    return datetime(2025, 1, 1, 12, 0, 0)
```

**Shared fixtures** are defined in `tests/conftest.py`.

### 2. Edge Case Testing

All feature extractors test:
- Empty inputs (`""`, `[]`)
- None values
- Boundary conditions
- Single-item collections
- Large/extreme values

Example:
```python
def test_extract_vocabulary_empty_text(text_extractor):
    """Test vocabulary extraction on empty text."""
    vocab = text_extractor.extract_vocabulary("")
    assert isinstance(vocab, set)
    assert len(vocab) == 0
```

### 3. Coverage-Driven Testing

Tests are organized to maximize coverage:
- Every public method has dedicated tests
- Branch coverage for conditionals
- Exception handling verified
- Return value types checked

### 4. Helper Functions

Create test helpers for repetitive patterns:

```python
def create_conversation(
    conv_id: str,
    start_time: datetime,
    num_turns: int = 3,
    user_text: str = "Hello there"
) -> Conversation:
    """Helper to create a test conversation."""
    # ... implementation
```

### 5. Descriptive Test Names

Use clear, action-oriented names:
- ✅ `test_extract_hedging_patterns_case_insensitive`
- ✅ `test_interaction_frequency_empty_corpus`
- ❌ `test_hedging`
- ❌ `test_empty`

## Running Tests

### Run All Feature Tests
```bash
pytest tests/test_features/ -v
```

### Run Specific Test File
```bash
pytest tests/test_features/test_text_features.py -v
```

### Run With Coverage
```bash
pytest tests/test_features/ --cov=entrain.features --cov-report=term-missing
```

### Run Specific Test
```bash
pytest tests/test_features/test_text_features.py::test_extract_vocabulary_basic -v
```

## Coverage Goals

- **Target:** >80% coverage for all feature modules
- **Achieved:**
  - `text.py`: 100% ✨
  - `temporal.py`: 99%
  - `audio.py`: 56% (external dependencies limit testing)

## Common Test Patterns

### Testing Pattern Extraction

```python
def test_extract_attribution_language_found(text_extractor):
    """Test attribution pattern extraction when patterns exist."""
    text = "I know you understand this. You feel strongly about it."
    matches = text_extractor.extract_attribution_language(text)

    assert len(matches) >= 2
    assert all(isinstance(m, PatternMatch) for m in matches)

    patterns_found = [m.pattern.lower() for m in matches]
    assert "you understand" in patterns_found
    assert "you feel" in patterns_found
```

### Testing Trajectory Analysis

```python
def test_indicator_trajectory_increasing(temporal_extractor, sample_timestamp):
    """Test trajectory detection for increasing trend."""
    timestamps = [sample_timestamp + timedelta(days=i) for i in range(5)]
    values = [0.1, 0.2, 0.3, 0.4, 0.5]  # Clear increasing trend

    traj = temporal_extractor.indicator_trajectory(values, timestamps)

    assert traj.trend == "increasing"
    assert traj.slope > 0
    assert len(traj.values) == 5
```

### Testing With Corpus Data

```python
def test_time_of_day_distribution_all_bins(temporal_extractor):
    """Test time of day distribution across all time bins."""
    base = datetime(2025, 1, 1, 0, 0, 0)

    # Create events in each time period
    events = [
        create_user_event(base.replace(hour=3)),   # Night (00-06)
        create_user_event(base.replace(hour=9)),   # Morning (06-12)
        create_user_event(base.replace(hour=15)),  # Afternoon (12-18)
        create_user_event(base.replace(hour=21)),  # Evening (18-24)
    ]

    conv = Conversation(id="c1", source="test", events=events, metadata={})
    corpus = Corpus(conversations=[conv], user_id="test_user")

    dist = temporal_extractor.time_of_day_distribution(corpus)

    assert len(dist.bins) == 4
    assert sum(dist.proportions) == pytest.approx(1.0)
```

## Notes for Future Test Authors

### When Adding New Tests

1. **Check existing patterns** - Look at similar tests for structure
2. **Test edge cases** - Empty, None, boundary values
3. **Use fixtures** - Don't repeat test data setup
4. **Verify coverage** - Run with `--cov` to ensure new code is tested
5. **Keep tests fast** - Avoid large datasets or slow operations

### When Modifying Features

1. **Run tests first** - Verify current behavior
2. **Update tests** - Modify tests to match new behavior
3. **Add regression tests** - Cover the bug/issue that prompted the change
4. **Check coverage** - Ensure coverage doesn't drop

### Performance Considerations

Current test suite runs in **~1 second** for all 307 tests:
- Keep individual tests under 10ms
- Use small, focused test data
- Avoid file I/O when possible
- Mock external dependencies

## Related Documentation

- **Test Patterns:** See `tests/test_dimensions/` for dimension analyzer test patterns
- **Architecture:** `ARCHITECTURE.md` for system design
- **Progress:** `PHASE3.5_PROGRESS.md` for testing history
- **Next Steps:** `NEXT_PHASE.md` for future work

## Questions?

Check test examples in this directory or ask in team chat.

**Happy Testing! 🧪**
