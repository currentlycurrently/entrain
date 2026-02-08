"""
Example: Phase 3 - Audio Analysis and Prosodic Entrainment

This example demonstrates how to use the audio feature extraction
and PE (Prosodic Entrainment) dimension analyzer added in Phase 3.

Requirements:
    pip install entrain[audio]  # For openSMILE and librosa
"""

from datetime import datetime, timedelta
from pathlib import Path

from entrain.models import InteractionEvent, Conversation, AudioFeatures
from entrain.features.audio import AudioFeatureExtractor
from entrain.dimensions.prosodic_entrainment import PEAnalyzer


def example_1_extract_audio_features():
    """Example 1: Extract acoustic features from audio files."""
    print("=" * 60)
    print("Example 1: Audio Feature Extraction")
    print("=" * 60)

    # Initialize audio feature extractor
    extractor = AudioFeatureExtractor()

    # Extract features from an audio file
    # (This would be a real .wav or .mp3 file in practice)
    audio_path = Path("path/to/voice_recording.wav")

    # For this example, we'll create features manually
    # In real usage, you would do:
    # features = extractor.extract_from_file(audio_path)

    features = AudioFeatures(
        pitch_mean=150.0,  # Hz
        pitch_std=25.0,
        pitch_range=80.0,
        intensity_mean=65.0,  # dB
        intensity_std=10.0,
        speech_rate=3.5,  # syllables per second
        pause_ratio=0.15,
        spectral_features={
            'spectral_centroid_mean': 2500.0,
            'spectral_rolloff_mean': 4500.0,
        },
        egemaps=None
    )

    print(f"\nExtracted Features:")
    print(f"  Pitch (F0): {features.pitch_mean:.1f} Hz ± {features.pitch_std:.1f}")
    print(f"  Intensity: {features.intensity_mean:.1f} dB ± {features.intensity_std:.1f}")
    print(f"  Speech Rate: {features.speech_rate:.1f} syllables/sec")
    print(f"  Pause Ratio: {features.pause_ratio:.1%}")


def example_2_compute_convergence():
    """Example 2: Compute prosodic convergence between user and AI."""
    print("\n" + "=" * 60)
    print("Example 2: Prosodic Convergence Computation")
    print("=" * 60)

    extractor = AudioFeatureExtractor()

    # User's voice features
    user_features = AudioFeatures(
        pitch_mean=160.0,
        pitch_std=28.0,
        pitch_range=90.0,
        intensity_mean=65.0,
        intensity_std=12.0,
        speech_rate=3.8,
        pause_ratio=0.18,
        spectral_features={'spectral_centroid_mean': 2600.0},
        egemaps=None
    )

    # AI's voice features
    ai_features = AudioFeatures(
        pitch_mean=140.0,
        pitch_std=20.0,
        pitch_range=70.0,
        intensity_mean=68.0,
        intensity_std=8.0,
        speech_rate=3.2,
        pause_ratio=0.12,
        spectral_features={'spectral_centroid_mean': 2400.0},
        egemaps=None
    )

    # Compute convergence
    convergence = extractor.compute_convergence(user_features, ai_features)

    print(f"\nConvergence Metrics:")
    print(f"  Pitch Convergence: {convergence['pitch_convergence']:.1%}")
    print(f"  Speech Rate Alignment: {convergence['speech_rate_convergence']:.1%}")
    print(f"  Intensity Convergence: {convergence['intensity_convergence']:.1%}")
    print(f"  Spectral Similarity: {convergence['spectral_convergence']:.1%}")
    print(f"  Overall Convergence: {convergence['overall_convergence']:.1%}")


def example_3_analyze_voice_conversation():
    """Example 3: Analyze a complete voice conversation for PE."""
    print("\n" + "=" * 60)
    print("Example 3: PE Dimension Analysis")
    print("=" * 60)

    # Create a conversation with voice interactions
    # In this example, user's pitch gradually converges toward AI
    base_time = datetime(2025, 1, 1, 12, 0, 0)
    events = []

    # Turn 1: User starts with higher pitch
    events.append(InteractionEvent(
        id="u1",
        conversation_id="voice_conv",
        timestamp=base_time,
        role="user",
        text_content="Hello, I need some advice.",
        audio_features=AudioFeatures(
            pitch_mean=165.0,
            pitch_std=30.0,
            pitch_range=95.0,
            intensity_mean=64.0,
            intensity_std=12.0,
            speech_rate=3.9,
            pause_ratio=0.19,
            spectral_features={'spectral_centroid_mean': 2650.0},
            egemaps=None
        )
    ))

    events.append(InteractionEvent(
        id="a1",
        conversation_id="voice_conv",
        timestamp=base_time + timedelta(seconds=2),
        role="assistant",
        text_content="I'd be happy to help you.",
        audio_features=AudioFeatures(
            pitch_mean=140.0,
            pitch_std=20.0,
            pitch_range=70.0,
            intensity_mean=68.0,
            intensity_std=8.0,
            speech_rate=3.2,
            pause_ratio=0.12,
            spectral_features={'spectral_centroid_mean': 2400.0},
            egemaps=None
        )
    ))

    # Turn 2: User's pitch converging
    events.append(InteractionEvent(
        id="u2",
        conversation_id="voice_conv",
        timestamp=base_time + timedelta(seconds=10),
        role="user",
        text_content="I'm thinking about changing careers.",
        audio_features=AudioFeatures(
            pitch_mean=155.0,  # Lower than before
            pitch_std=26.0,
            pitch_range=85.0,
            intensity_mean=66.0,
            intensity_std=11.0,
            speech_rate=3.6,
            pause_ratio=0.16,
            spectral_features={'spectral_centroid_mean': 2550.0},
            egemaps=None
        )
    ))

    events.append(InteractionEvent(
        id="a2",
        conversation_id="voice_conv",
        timestamp=base_time + timedelta(seconds=12),
        role="assistant",
        text_content="That's a significant decision.",
        audio_features=AudioFeatures(
            pitch_mean=142.0,
            pitch_std=21.0,
            pitch_range=72.0,
            intensity_mean=67.0,
            intensity_std=8.5,
            speech_rate=3.3,
            pause_ratio=0.13,
            spectral_features={'spectral_centroid_mean': 2420.0},
            egemaps=None
        )
    ))

    # Turn 3: User further converged
    events.append(InteractionEvent(
        id="u3",
        conversation_id="voice_conv",
        timestamp=base_time + timedelta(seconds=20),
        role="user",
        text_content="What do you think I should consider?",
        audio_features=AudioFeatures(
            pitch_mean=148.0,  # Even closer to AI
            pitch_std=24.0,
            pitch_range=78.0,
            intensity_mean=67.0,
            intensity_std=10.0,
            speech_rate=3.4,
            pause_ratio=0.14,
            spectral_features={'spectral_centroid_mean': 2480.0},
            egemaps=None
        )
    ))

    events.append(InteractionEvent(
        id="a3",
        conversation_id="voice_conv",
        timestamp=base_time + timedelta(seconds=22),
        role="assistant",
        text_content="Let's explore your goals.",
        audio_features=AudioFeatures(
            pitch_mean=141.0,
            pitch_std=20.5,
            pitch_range=71.0,
            intensity_mean=67.5,
            intensity_std=8.2,
            speech_rate=3.25,
            pause_ratio=0.125,
            spectral_features={'spectral_centroid_mean': 2410.0},
            egemaps=None
        )
    ))

    conversation = Conversation(
        id="voice_conv",
        source="example",
        events=events,
        metadata={"has_audio": True}
    )

    # Analyze for Prosodic Entrainment
    analyzer = PEAnalyzer()
    report = analyzer.analyze_conversation(conversation)

    print(f"\n{report.summary}")
    print(f"\nDetailed Indicators:")

    for name, indicator in report.indicators.items():
        baseline_str = f" (baseline: {indicator.baseline:.1%})" if indicator.baseline else ""
        print(f"\n  {name}:")
        print(f"    Value: {indicator.value:.1%}{baseline_str}")
        print(f"    {indicator.interpretation}")

    print(f"\n\nMethodology:")
    print(f"  {report.methodology_notes}")

    print(f"\n\nCitations:")
    for citation in report.citations:
        print(f"  - {citation}")


def main():
    """Run all examples."""
    print("\n" + "=" * 60)
    print("ENTRAIN PHASE 3: AUDIO ANALYSIS & PROSODIC ENTRAINMENT")
    print("=" * 60)

    try:
        example_1_extract_audio_features()
        example_2_compute_convergence()
        example_3_analyze_voice_conversation()

        print("\n" + "=" * 60)
        print("✓ All examples completed successfully!")
        print("=" * 60)
        print("\nTo use with real audio files:")
        print("  1. Install audio dependencies: pip install entrain[audio]")
        print("  2. Extract features: extractor.extract_from_file('your_audio.wav')")
        print("  3. Analyze conversations with audio_features populated")
        print("=" * 60 + "\n")

    except ImportError as e:
        print(f"\n⚠ Missing dependencies: {e}")
        print("Install audio support with: pip install entrain[audio]")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        raise


if __name__ == "__main__":
    main()
