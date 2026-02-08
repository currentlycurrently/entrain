"""
Command-line interface for the Entrain Reference Library.

Provides commands for parsing chat exports, running dimension analyzers,
and generating reports.

See ARCHITECTURE.md Section 7 for specification.
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

from entrain.models import ENTRAIN_VERSION, EntrainReport
from entrain.parsers import get_default_registry
from entrain.dimensions import (
    SRAnalyzer,
    LCAnalyzer,
    AEAnalyzer,
    RCDAnalyzer,
    DFAnalyzer,
)
from entrain.reporting import JSONReportGenerator, MarkdownReportGenerator, CSVExporter


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser for the CLI."""
    parser = argparse.ArgumentParser(
        prog="entrain",
        description="Entrain Framework: Measure AI cognitive influence on humans",
        epilog="For more information: https://entrain.institute"
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"Entrain Reference Library v{ENTRAIN_VERSION}"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Parse command
    parse_parser = subparsers.add_parser(
        "parse",
        help="Parse and validate a chat export file"
    )
    parse_parser.add_argument(
        "export_file",
        type=Path,
        help="Path to chat export file (ZIP or JSON)"
    )

    # Analyze command
    analyze_parser = subparsers.add_parser(
        "analyze",
        help="Analyze conversations for cognitive influence dimensions"
    )
    analyze_parser.add_argument(
        "export_file",
        type=Path,
        help="Path to chat export file"
    )
    analyze_parser.add_argument(
        "--dim",
        choices=["SR", "LC", "AE", "RCD", "DF"],
        help="Analyze specific dimension only"
    )
    analyze_parser.add_argument(
        "--corpus",
        action="store_true",
        help="Analyze entire corpus (default: first conversation only)"
    )

    # Report command
    report_parser = subparsers.add_parser(
        "report",
        help="Generate formatted report from analysis"
    )
    report_parser.add_argument(
        "export_file",
        type=Path,
        help="Path to chat export file"
    )
    report_parser.add_argument(
        "-o", "--output",
        type=Path,
        help="Output file path (default: stdout)"
    )
    report_parser.add_argument(
        "--format",
        choices=["markdown", "json", "csv"],
        default="markdown",
        help="Report format (default: markdown)"
    )
    report_parser.add_argument(
        "--dim",
        choices=["SR", "LC", "AE", "RCD", "DF"],
        help="Analyze specific dimension only"
    )

    # Info command
    info_parser = subparsers.add_parser(
        "info",
        help="Show framework version and available dimensions"
    )

    return parser


def cmd_parse(args: argparse.Namespace) -> int:
    """Handle parse command."""
    export_file = args.export_file

    if not export_file.exists():
        print(f"Error: File not found: {export_file}", file=sys.stderr)
        return 1

    # Set up parser registry with all available parsers
    registry = get_default_registry()

    # Try to parse
    try:
        print(f"Parsing {export_file}...")
        corpus = registry.parse_auto(export_file)

        print(f"✓ Successfully parsed {len(corpus.conversations)} conversations")
        print(f"  Total events: {sum(len(c.events) for c in corpus.conversations)}")
        print(f"  Date range: {corpus.date_range[0].date() if corpus.date_range else 'N/A'} "
              f"to {corpus.date_range[1].date() if corpus.date_range else 'N/A'}")

        return 0

    except Exception as e:
        print(f"✗ Parse failed: {e}", file=sys.stderr)
        return 1


def cmd_analyze(args: argparse.Namespace) -> int:
    """Handle analyze command."""
    export_file = args.export_file

    if not export_file.exists():
        print(f"Error: File not found: {export_file}", file=sys.stderr)
        return 1

    # Parse file with all available parsers
    registry = get_default_registry()

    try:
        print(f"Parsing {export_file}...")
        corpus = registry.parse_auto(export_file)
        print(f"✓ Parsed {len(corpus.conversations)} conversations\n")

    except Exception as e:
        print(f"✗ Parse failed: {e}", file=sys.stderr)
        return 1

    # Select analyzers
    analyzers = {}

    if args.dim:
        # Specific dimension
        analyzer_map = {
            "SR": SRAnalyzer(),
            "LC": LCAnalyzer(),
            "AE": AEAnalyzer(),
            "RCD": RCDAnalyzer(),
            "DF": DFAnalyzer(),
        }
        analyzers[args.dim] = analyzer_map[args.dim]
    else:
        # All dimensions
        analyzers = {
            "SR": SRAnalyzer(),
            "LC": LCAnalyzer(),
            "AE": AEAnalyzer(),
            "RCD": RCDAnalyzer(),
            "DF": DFAnalyzer(),
        }

    # Run analysis
    results = {}

    for dim_code, analyzer in analyzers.items():
        try:
            print(f"Analyzing {dim_code} ({analyzer.dimension_name})...")

            if args.corpus:
                report = analyzer.analyze_corpus(corpus)
            else:
                if not corpus.conversations:
                    print(f"  ✗ No conversations to analyze", file=sys.stderr)
                    continue
                report = analyzer.analyze_conversation(corpus.conversations[0])

            results[dim_code] = report
            print(f"  ✓ {report.summary}\n")

        except Exception as e:
            print(f"  ✗ Analysis failed: {e}\n", file=sys.stderr)
            continue

    if not results:
        print("No analyses completed successfully", file=sys.stderr)
        return 1

    # Show results summary
    print("\n" + "="*60)
    print("ANALYSIS SUMMARY")
    print("="*60 + "\n")

    for dim_code, report in results.items():
        print(f"{dim_code}: {report.summary}")

        for name, indicator in report.indicators.items():
            baseline_str = f" (baseline: {indicator.baseline:.3f})" if indicator.baseline else ""
            print(f"  • {name}: {indicator.value:.3f}{baseline_str}")

        print()

    return 0


def cmd_report(args: argparse.Namespace) -> int:
    """Handle report command."""
    export_file = args.export_file

    if not export_file.exists():
        print(f"Error: File not found: {export_file}", file=sys.stderr)
        return 1

    # Parse file with all available parsers
    registry = get_default_registry()

    try:
        corpus = registry.parse_auto(export_file)
    except Exception as e:
        print(f"Parse failed: {e}", file=sys.stderr)
        return 1

    # Select analyzers
    if args.dim:
        analyzer_map = {
            "SR": SRAnalyzer(),
            "LC": LCAnalyzer(),
            "AE": AEAnalyzer(),
            "RCD": RCDAnalyzer(),
            "DF": DFAnalyzer(),
        }
        analyzers = {args.dim: analyzer_map[args.dim]}
    else:
        analyzers = {
            "SR": SRAnalyzer(),
            "LC": LCAnalyzer(),
            "AE": AEAnalyzer(),
            "RCD": RCDAnalyzer(),
            "DF": DFAnalyzer(),
        }

    # Run analysis
    dimension_reports = {}

    for dim_code, analyzer in analyzers.items():
        try:
            # Use corpus analysis for DF, conversation for others
            if dim_code == "DF":
                report = analyzer.analyze_corpus(corpus)
            else:
                if corpus.conversations:
                    report = analyzer.analyze_conversation(corpus.conversations[0])
                else:
                    continue

            dimension_reports[dim_code] = report

        except Exception as e:
            print(f"Warning: {dim_code} analysis failed: {e}", file=sys.stderr)
            continue

    if not dimension_reports:
        print("No analyses completed successfully", file=sys.stderr)
        return 1

    # Create EntrainReport
    entrain_report = EntrainReport(
        version=ENTRAIN_VERSION,
        generated_at=datetime.now(),
        input_summary={
            "conversations": len(corpus.conversations),
            "total_events": sum(len(c.events) for c in corpus.conversations),
            "source": corpus.conversations[0].source if corpus.conversations else "unknown",
        },
        dimensions=dimension_reports,
        methodology="Text-based analysis using Entrain Reference Library v" + ENTRAIN_VERSION
    )

    # Generate report
    if args.format == "json":
        generator = JSONReportGenerator()
        output = generator.generate(entrain_report)

        # Write output
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(output)
            print(f"Report written to {args.output}")
        else:
            print(output)

    elif args.format == "csv":
        if not args.output:
            print("Error: CSV format requires --output/-o to specify output file", file=sys.stderr)
            return 1

        exporter = CSVExporter()
        exporter.export_indicators_summary(entrain_report, args.output)
        print(f"CSV report written to {args.output}")

    else:  # markdown
        generator = MarkdownReportGenerator()
        output = generator.generate(entrain_report)

        # Write output
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(output)
            print(f"Report written to {args.output}")
        else:
            print(output)

    return 0


def cmd_info(args: argparse.Namespace) -> int:
    """Handle info command."""
    print(f"Entrain Reference Library v{ENTRAIN_VERSION}")
    print("\nThe Entrain Framework measures AI cognitive influence on humans.")
    print("\nAvailable Dimensions:")
    print("  SR  - Sycophantic Reinforcement")
    print("  PE  - Prosodic Entrainment (Phase 3)")
    print("  LC  - Linguistic Convergence")
    print("  AE  - Autonomy Erosion")
    print("  RCD - Reality Coherence Disruption")
    print("  DF  - Dependency Formation")
    print("\nSupported Platforms:")
    print("  • ChatGPT (JSON/ZIP export)")
    print("  • Claude (JSON/JSONL export, browser extensions)")
    print("  • Character.AI (JSON export)")
    print("  • Generic CSV/JSON (any platform with role/content format)")
    print("\nFor more information: https://entrain.institute")
    print("Documentation: docs/FRAMEWORK.md, docs/ARCHITECTURE.md")

    return 0


def main() -> int:
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    # Dispatch to command handlers
    commands = {
        "parse": cmd_parse,
        "analyze": cmd_analyze,
        "report": cmd_report,
        "info": cmd_info,
    }

    handler = commands.get(args.command)
    if handler:
        return handler(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
