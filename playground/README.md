# Playground Directory

This directory is for local testing and experimentation. **It is gitignored** - nothing here will be committed to the repository.

## Purpose

Use this directory to:
- Test the library with your real conversation exports
- Generate reports without cluttering the project root
- Experiment with different analysis configurations
- Store temporary data files

## Example Workflow

```bash
# 1. Copy your ChatGPT export here
cp ~/Downloads/conversations.json playground/

# 2. Parse and validate (from project root)
python3 -m entrain.cli parse playground/conversations.json

# 3. Run analysis
python3 -m entrain.cli analyze playground/conversations.json --dim SR

# 4. Generate full report
python3 -m entrain.cli report playground/conversations.json -o playground/my_report.md

# 5. Generate CSV time series
python3 -m entrain.cli report playground/conversations.json -o playground/timeseries.csv --format csv
```

## Suggested Structure

```
playground/
├── README.md           # This file (tracked in git)
├── conversations.json  # Your ChatGPT export (gitignored)
├── reports/           # Generated reports (gitignored)
│   ├── full_report.md
│   ├── sr_report.json
│   └── timeseries.csv
└── experiments/       # Test scripts (gitignored)
    └── custom_analysis.py
```

## Privacy Note

This entire directory (except this README) is gitignored to protect your privacy. Your conversation data will never be committed to the repository.

## Pro Tips

1. **Keep it organized**: Create subdirectories for different experiments
2. **Name your reports clearly**: Include dates and dimension codes
3. **Test synthetic data first**: Run `python3 examples/synthetic_conversation.py` before using real data
4. **Multiple exports**: You can analyze multiple conversation files by placing them in subdirectories

## Example: Analyzing Multiple Exports

```bash
# Create subdirectories for different time periods
mkdir -p playground/2024-q1 playground/2024-q2

# Analyze each period separately
python3 -m entrain.cli analyze playground/2024-q1/conversations.json -o playground/2024-q1/report.md
python3 -m entrain.cli analyze playground/2024-q2/conversations.json -o playground/2024-q2/report.md
```
