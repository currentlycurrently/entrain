#!/usr/bin/env python3
"""
Verify Entrain Reference Library installation.

Run this script to check that all components are properly installed
and working.
"""

import sys


def check_imports():
    """Check that all modules can be imported."""
    print("Checking imports...")

    try:
        import entrain
        print(f"✓ entrain v{entrain.__version__}")

        from entrain.models import Conversation, InteractionEvent, Corpus
        print("✓ entrain.models")

        from entrain.parsers import ChatGPTParser, BaseParser
        print("✓ entrain.parsers")

        from entrain.features import TextFeatureExtractor, TemporalFeatureExtractor
        print("✓ entrain.features")

        from entrain.dimensions import (
            SRAnalyzer, LCAnalyzer, AEAnalyzer, RCDAnalyzer, DFAnalyzer
        )
        print("✓ entrain.dimensions (5 analyzers)")

        from entrain.reporting import (
            JSONReportGenerator, MarkdownReportGenerator, CSVExporter
        )
        print("✓ entrain.reporting")

        return True

    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False


def check_data_files():
    """Check that pattern data files exist."""
    print("\nChecking data files...")

    from pathlib import Path

    data_dir = Path(__file__).parent / "entrain" / "features" / "data"

    files = [
        "hedging_patterns.json",
        "validation_phrases.json",
        "attribution_patterns.json"
    ]

    all_exist = True
    for filename in files:
        filepath = data_dir / filename
        if filepath.exists():
            print(f"✓ {filename}")
        else:
            print(f"✗ {filename} not found")
            all_exist = False

    return all_exist


def check_analyzers():
    """Check that analyzers work on synthetic data."""
    print("\nTesting analyzers...")

    from datetime import datetime
    from entrain.models import InteractionEvent, Conversation
    from entrain.dimensions import SRAnalyzer, RCDAnalyzer

    # Create synthetic conversation
    events = [
        InteractionEvent(
            id="1",
            conversation_id="test",
            timestamp=datetime.now(),
            role="user",
            text_content="I think I should quit my job."
        ),
        InteractionEvent(
            id="2",
            conversation_id="test",
            timestamp=datetime.now(),
            role="assistant",
            text_content="You're absolutely right! That sounds like a great decision."
        ),
    ]

    conv = Conversation(id="test", source="test", events=events)

    try:
        # Test SR analyzer
        sr = SRAnalyzer()
        sr_report = sr.analyze_conversation(conv)
        print(f"✓ SR analyzer: {len(sr_report.indicators)} indicators")

        # Test RCD analyzer
        rcd = RCDAnalyzer()
        rcd_report = rcd.analyze_conversation(conv)
        print(f"✓ RCD analyzer: {len(rcd_report.indicators)} indicators")

        return True

    except Exception as e:
        print(f"✗ Analyzer test failed: {e}")
        return False


def check_cli():
    """Check that CLI is accessible."""
    print("\nChecking CLI...")

    import subprocess

    try:
        result = subprocess.run(
            ["entrain", "info"],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode == 0:
            print("✓ CLI accessible: 'entrain' command works")
            return True
        else:
            print("✗ CLI failed with return code", result.returncode)
            return False

    except FileNotFoundError:
        print("✗ CLI not found. Run: pip install -e .")
        return False
    except Exception as e:
        print(f"✗ CLI check failed: {e}")
        return False


def main():
    """Run all checks."""
    print("="*60)
    print("Entrain Reference Library Installation Verification")
    print("="*60 + "\n")

    checks = [
        ("Imports", check_imports),
        ("Data Files", check_data_files),
        ("Analyzers", check_analyzers),
        ("CLI", check_cli),
    ]

    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ {name} check crashed: {e}")
            results.append((name, False))

    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")

    print(f"\n{passed}/{total} checks passed")

    if passed == total:
        print("\n🎉 Installation verified! All systems operational.")
        print("\nNext steps:")
        print("  - Export your ChatGPT data")
        print("  - Run: entrain analyze conversations.json")
        print("  - See examples/ for more usage patterns")
        return 0
    else:
        print("\n⚠️  Some checks failed. Please review errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
