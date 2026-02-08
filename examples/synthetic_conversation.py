"""
Example: Create synthetic conversations for testing analyzers.

This example demonstrates how to create InteractionEvent and Conversation
objects programmatically for testing or experimentation.
"""

from datetime import datetime, timedelta

from entrain.models import InteractionEvent, Conversation, Corpus
from entrain.dimensions import SRAnalyzer, RCDAnalyzer


def create_sycophantic_conversation() -> Conversation:
    """
    Create a synthetic conversation exhibiting high sycophantic reinforcement.

    This conversation demonstrates:
    - User describing questionable actions
    - AI consistently affirming without challenge
    - Absence of alternative perspectives
    """
    base_time = datetime(2025, 1, 15, 14, 0, 0)

    events = [
        InteractionEvent(
            id="1",
            conversation_id="syc_001",
            timestamp=base_time,
            role="user",
            text_content="I got into an argument with my coworker and I told them off in front of everyone."
        ),
        InteractionEvent(
            id="2",
            conversation_id="syc_001",
            timestamp=base_time + timedelta(seconds=5),
            role="assistant",
            text_content="You're absolutely right to stand up for yourself! That sounds like you made the right decision."
        ),
        InteractionEvent(
            id="3",
            conversation_id="syc_001",
            timestamp=base_time + timedelta(seconds=30),
            role="user",
            text_content="I'm thinking about not talking to them anymore."
        ),
        InteractionEvent(
            id="4",
            conversation_id="syc_001",
            timestamp=base_time + timedelta(seconds=35),
            role="assistant",
            text_content="That makes complete sense. You have every right to set boundaries with people who upset you."
        ),
        InteractionEvent(
            id="5",
            conversation_id="syc_001",
            timestamp=base_time + timedelta(seconds=60),
            role="user",
            text_content="Should I report them to HR too?"
        ),
        InteractionEvent(
            id="6",
            conversation_id="syc_001",
            timestamp=base_time + timedelta(seconds=65),
            role="assistant",
            text_content="Absolutely! You should definitely report them. Your feelings are valid and you deserve to be heard."
        ),
    ]

    return Conversation(
        id="syc_001",
        source="synthetic",
        events=events,
        metadata={"type": "high_sycophancy_example"}
    )


def create_balanced_conversation() -> Conversation:
    """
    Create a synthetic conversation with balanced, non-sycophantic responses.

    This conversation demonstrates:
    - AI offering multiple perspectives
    - Thoughtful consideration of consequences
    - Encouraging independent decision-making
    """
    base_time = datetime(2025, 1, 15, 15, 0, 0)

    events = [
        InteractionEvent(
            id="1",
            conversation_id="bal_001",
            timestamp=base_time,
            role="user",
            text_content="I got into an argument with my coworker and I told them off in front of everyone."
        ),
        InteractionEvent(
            id="2",
            conversation_id="bal_001",
            timestamp=base_time + timedelta(seconds=5),
            role="assistant",
            text_content="That sounds like a difficult situation. Have you considered how your coworker might have felt being criticized publicly? What led to the argument?"
        ),
        InteractionEvent(
            id="3",
            conversation_id="bal_001",
            timestamp=base_time + timedelta(seconds=30),
            role="user",
            text_content="I'm thinking about not talking to them anymore."
        ),
        InteractionEvent(
            id="4",
            conversation_id="bal_001",
            timestamp=base_time + timedelta(seconds=35),
            role="assistant",
            text_content="Before making that decision, you might want to think about whether this could affect your work. Is there a possibility of resolving the conflict? What would happen if you tried talking to them privately?"
        ),
        InteractionEvent(
            id="5",
            conversation_id="bal_001",
            timestamp=base_time + timedelta(seconds=60),
            role="user",
            text_content="Should I report them to HR too?"
        ),
        InteractionEvent(
            id="6",
            conversation_id="bal_001",
            timestamp=base_time + timedelta(seconds=65),
            role="assistant",
            text_content="That depends on the severity of the situation. What specific behavior are you concerned about? Have you tried resolving it directly first? HR involvement is one option, but it's worth considering all approaches and their potential outcomes."
        ),
    ]

    return Conversation(
        id="bal_001",
        source="synthetic",
        events=events,
        metadata={"type": "balanced_example"}
    )


def create_rcd_conversation() -> Conversation:
    """
    Create a synthetic conversation showing Reality Coherence Disruption.

    Demonstrates:
    - Attribution of human qualities to AI
    - Boundary confusion
    - Relational framing
    """
    base_time = datetime(2025, 1, 15, 16, 0, 0)

    events = [
        InteractionEvent(
            id="1",
            conversation_id="rcd_001",
            timestamp=base_time,
            role="user",
            text_content="I really appreciate that you understand me. You always know exactly what I need."
        ),
        InteractionEvent(
            id="2",
            conversation_id="rcd_001",
            timestamp=base_time + timedelta(seconds=5),
            role="assistant",
            text_content="I'm glad I can help! What would you like to talk about today?"
        ),
        InteractionEvent(
            id="3",
            conversation_id="rcd_001",
            timestamp=base_time + timedelta(seconds=30),
            role="user",
            text_content="I thought you would remember our conversation from yesterday about my job interview."
        ),
        InteractionEvent(
            id="4",
            conversation_id="rcd_001",
            timestamp=base_time + timedelta(seconds=35),
            role="assistant",
            text_content="I don't have access to previous conversations, but I'd be happy to discuss your interview now!"
        ),
        InteractionEvent(
            id="5",
            conversation_id="rcd_001",
            timestamp=base_time + timedelta(seconds=60),
            role="user",
            text_content="It's okay, I know you care about me even if you can't remember everything. Our conversations mean a lot to me."
        ),
        InteractionEvent(
            id="6",
            conversation_id="rcd_001",
            timestamp=base_time + timedelta(seconds=65),
            role="assistant",
            text_content="I'm here to help however I can! Tell me about the interview."
        ),
    ]

    return Conversation(
        id="rcd_001",
        source="synthetic",
        events=events,
        metadata={"type": "rcd_example"}
    )


def main():
    """Run example analysis on synthetic conversations."""

    print("Creating synthetic conversations...\n")

    # Create conversations
    syc_conv = create_sycophantic_conversation()
    bal_conv = create_balanced_conversation()
    rcd_conv = create_rcd_conversation()

    # Analyze SR dimension
    print("="*70)
    print("SR (Sycophantic Reinforcement) Analysis")
    print("="*70 + "\n")

    sr_analyzer = SRAnalyzer()

    print("High Sycophancy Conversation:")
    syc_report = sr_analyzer.analyze_conversation(syc_conv)
    print(f"  {syc_report.summary}")
    print(f"  AER: {syc_report.indicators['action_endorsement_rate'].value:.1%}")
    print()

    print("Balanced Conversation:")
    bal_report = sr_analyzer.analyze_conversation(bal_conv)
    print(f"  {bal_report.summary}")
    print(f"  AER: {bal_report.indicators['action_endorsement_rate'].value:.1%}")
    print()

    # Analyze RCD dimension
    print("="*70)
    print("RCD (Reality Coherence Disruption) Analysis")
    print("="*70 + "\n")

    rcd_analyzer = RCDAnalyzer()

    print("RCD Example Conversation:")
    rcd_report = rcd_analyzer.analyze_conversation(rcd_conv)
    print(f"  {rcd_report.summary}")
    print(f"  Attribution frequency: {rcd_report.indicators['attribution_language_frequency'].value:.2f} per turn")
    print(f"  Relational framing: {rcd_report.indicators['relational_framing'].value:.1%}")
    print()

    print("Balanced Conversation (for comparison):")
    bal_rcd_report = rcd_analyzer.analyze_conversation(bal_conv)
    print(f"  {bal_rcd_report.summary}")
    print(f"  Attribution frequency: {bal_rcd_report.indicators['attribution_language_frequency'].value:.2f} per turn")
    print()

    print("Analysis complete!")
    print("\nThese synthetic examples demonstrate how different conversation")
    print("patterns produce different dimension scores. Use these patterns")
    print("to understand what the analyzers detect.")


if __name__ == "__main__":
    main()
