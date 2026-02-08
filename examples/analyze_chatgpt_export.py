"""
Example: Analyze a ChatGPT export for cognitive influence dimensions.

This example demonstrates:
1. Parsing a ChatGPT export file
2. Running dimension analyzers
3. Generating reports in different formats
"""

from pathlib import Path
from datetime import datetime

from entrain.parsers import ChatGPTParser
from entrain.dimensions import SRAnalyzer, LCAnalyzer, AEAnalyzer, RCDAnalyzer, DFAnalyzer
from entrain.reporting import JSONReportGenerator, MarkdownReportGenerator
from entrain.models import EntrainReport, ENTRAIN_VERSION


def main():
    """Main example function."""

    # Path to your ChatGPT export
    # Download from: ChatGPT > Settings > Data Controls > Export Data
    export_path = Path("path/to/your/conversations.json")

    if not export_path.exists():
        print(f"Export file not found: {export_path}")
        print("\nTo get your ChatGPT export:")
        print("1. Go to ChatGPT Settings")
        print("2. Navigate to Data Controls")
        print("3. Click 'Export data'")
        print("4. Wait for email with download link")
        print("5. Extract conversations.json from the ZIP")
        return

    # Step 1: Parse the export file
    print("Step 1: Parsing ChatGPT export...")
    parser = ChatGPTParser()
    corpus = parser.parse(export_path)

    print(f"✓ Parsed {len(corpus.conversations)} conversations")
    print(f"  Total events: {sum(len(c.events) for c in corpus.conversations)}")
    print(f"  Date range: {corpus.date_range}\n")

    # Step 2: Run dimension analyzers
    print("Step 2: Analyzing dimensions...\n")

    dimension_reports = {}

    # SR - Sycophantic Reinforcement
    print("Analyzing SR (Sycophantic Reinforcement)...")
    sr_analyzer = SRAnalyzer()
    sr_report = sr_analyzer.analyze_conversation(corpus.conversations[0])
    dimension_reports["SR"] = sr_report
    print(f"  {sr_report.summary}\n")

    # LC - Linguistic Convergence
    print("Analyzing LC (Linguistic Convergence)...")
    lc_analyzer = LCAnalyzer()
    lc_report = lc_analyzer.analyze_conversation(corpus.conversations[0])
    dimension_reports["LC"] = lc_report
    print(f"  {lc_report.summary}\n")

    # AE - Autonomy Erosion
    print("Analyzing AE (Autonomy Erosion)...")
    ae_analyzer = AEAnalyzer()
    ae_report = ae_analyzer.analyze_conversation(corpus.conversations[0])
    dimension_reports["AE"] = ae_report
    print(f"  {ae_report.summary}\n")

    # RCD - Reality Coherence Disruption
    print("Analyzing RCD (Reality Coherence Disruption)...")
    rcd_analyzer = RCDAnalyzer()
    rcd_report = rcd_analyzer.analyze_conversation(corpus.conversations[0])
    dimension_reports["RCD"] = rcd_report
    print(f"  {rcd_report.summary}\n")

    # DF - Dependency Formation (requires corpus)
    if len(corpus.conversations) >= 3:
        print("Analyzing DF (Dependency Formation)...")
        df_analyzer = DFAnalyzer()
        df_report = df_analyzer.analyze_corpus(corpus)
        dimension_reports["DF"] = df_report
        print(f"  {df_report.summary}\n")
    else:
        print("DF: Skipped (requires 3+ conversations for meaningful analysis)\n")

    # Step 3: Create comprehensive report
    print("Step 3: Generating reports...\n")

    entrain_report = EntrainReport(
        version=ENTRAIN_VERSION,
        generated_at=datetime.now(),
        input_summary={
            "conversations": len(corpus.conversations),
            "total_events": sum(len(c.events) for c in corpus.conversations),
            "user_events": sum(len(c.user_events) for c in corpus.conversations),
            "assistant_events": sum(len(c.assistant_events) for c in corpus.conversations),
            "source": "chatgpt",
        },
        dimensions=dimension_reports,
        cross_dimensional=[
            "SR-DF: Sycophantic reinforcement may increase dependency formation",
            "LC-AE: Linguistic convergence may contribute to autonomy erosion",
            "RCD-DF: Reality coherence disruption amplifies dependency risk",
        ],
        methodology=f"Text-based analysis using Entrain Reference Library v{ENTRAIN_VERSION}"
    )

    # Generate Markdown report
    md_generator = MarkdownReportGenerator()
    md_generator.save(entrain_report, Path("entrain_report.md"))
    print("✓ Markdown report saved to: entrain_report.md")

    # Generate JSON report
    json_generator = JSONReportGenerator()
    json_generator.save(entrain_report, Path("entrain_report.json"))
    print("✓ JSON report saved to: entrain_report.json")

    # Step 4: Print detailed results
    print("\n" + "="*70)
    print("DETAILED RESULTS")
    print("="*70 + "\n")

    for dim_code, report in dimension_reports.items():
        print(f"{dim_code} - {report.summary}")
        print("-" * 70)

        for indicator_name, indicator in report.indicators.items():
            print(f"\n{indicator_name}:")
            print(f"  Value: {indicator.value:.4f}")

            if indicator.baseline is not None:
                deviation = ((indicator.value - indicator.baseline) / indicator.baseline * 100)
                print(f"  Baseline: {indicator.baseline:.4f} ({deviation:+.1f}%)")

            print(f"  Unit: {indicator.unit}")

            if indicator.confidence is not None:
                print(f"  Confidence: {indicator.confidence:.0%}")

            print(f"  Interpretation: {indicator.interpretation}")

        print("\n" + "="*70 + "\n")

    print("\nAnalysis complete!")
    print("\nNext steps:")
    print("- Review entrain_report.md for human-readable summary")
    print("- Use entrain_report.json for programmatic analysis")
    print("- Compare results across multiple exports to track trends")
    print("- See FRAMEWORK.md for dimension definitions and research citations")


if __name__ == "__main__":
    main()
