"""
data_validation.py — Data quality checks for LinkedIn analytics CSVs.

Supports both content analytics and follower metrics files.
"""

import pandas as pd
import sys


CONTENT_COLUMNS = [
    "Date", "Impressions (organic)", "Impressions (sponsored)", "Impressions (total)",
    "Unique impressions (organic)", "Clicks (organic)", "Clicks (sponsored)", "Clicks (total)",
    "Reactions (organic)", "Reactions (sponsored)", "Reactions (total)",
    "Comments (organic)", "Comments (sponsored)", "Comments (total)",
    "Reposts (organic)", "Reposts (sponsored)", "Reposts (total)",
    "Engagement rate (organic)", "Engagement rate (sponsored)", "Engagement rate (total)",
]

FOLLOWER_COLUMNS = [
    "Date", "Sponsored followers", "Organic followers", "Auto-invited followers", "Total followers",
]


def validate_csv(csv_path: str) -> dict:
    """Run all validation checks on the CSV file. Auto-detects content vs followers."""
    report = {"passed": True, "warnings": [], "errors": [], "summary": {}}

    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        report["passed"] = False
        report["errors"].append(f"Cannot read CSV: {e}")
        return report

    report["summary"]["rows"] = len(df)
    report["summary"]["columns"] = len(df.columns)

    # Auto-detect type
    if "Total followers" in df.columns:
        report["summary"]["type"] = "followers"
        required = FOLLOWER_COLUMNS
    elif "Impressions (total)" in df.columns:
        report["summary"]["type"] = "content"
        required = CONTENT_COLUMNS
    else:
        report["summary"]["type"] = "unknown"
        required = []
        report["warnings"].append("Could not auto-detect file type.")

    # Column check
    missing = [c for c in required if c not in df.columns]
    if missing:
        report["passed"] = False
        report["errors"].append(f"Missing columns: {missing}")

    # Null values
    total_nulls = df.isnull().sum().sum()
    if total_nulls > 0:
        cols_with_nulls = df.isnull().sum()[df.isnull().sum() > 0].to_dict()
        report["errors"].append(f"Null values: {cols_with_nulls}")
        report["passed"] = False
    else:
        report["summary"]["null_values"] = 0

    # Date check
    try:
        dates = pd.to_datetime(df["Date"], format="mixed")
        report["summary"]["date_range"] = f"{dates.min().date()} to {dates.max().date()}"
        report["summary"]["total_days"] = len(dates)
        dupes = dates.duplicated().sum()
        if dupes > 0:
            report["warnings"].append(f"Duplicate dates: {dupes}")
    except Exception as e:
        report["passed"] = False
        report["errors"].append(f"Date parsing error: {e}")

    # Type-specific checks
    if report["summary"]["type"] == "content":
        _validate_content(df, report)
    elif report["summary"]["type"] == "followers":
        _validate_followers(df, report)

    return report


def _validate_content(df, report):
    """Content-specific validation checks."""
    count_cols = ["Impressions (total)", "Clicks (total)", "Reactions (total)",
                  "Comments (total)", "Reposts (total)"]
    negatives = {}
    for col in count_cols:
        if col in df.columns:
            neg = (df[col] < 0).sum()
            if neg > 0:
                negatives[col] = int(neg)
    if negatives:
        report["warnings"].append(f"Negative values (LinkedIn corrections): {negatives}")

    if "Engagement rate (total)" in df.columns:
        out_of_range = ((df["Engagement rate (total)"] < 0) | (df["Engagement rate (total)"] > 1)).sum()
        if out_of_range > 0:
            report["warnings"].append(f"Engagement rates outside [0, 1]: {out_of_range} rows")

    sponsored_cols = [c for c in df.columns if "sponsored" in c.lower()]
    all_zero = all(df[c].sum() == 0 for c in sponsored_cols if c in df.columns)
    report["summary"]["has_sponsored_data"] = not all_zero


def _validate_followers(df, report):
    """Follower-specific validation checks."""
    total = df["Total followers"].sum()
    organic = df["Organic followers"].sum()
    sponsored = df["Sponsored followers"].sum()
    report["summary"]["total_followers_gained"] = int(total)
    report["summary"]["all_organic"] = sponsored == 0

    neg = (df["Total followers"] < 0).sum()
    if neg > 0:
        report["warnings"].append(f"Negative follower days (unfollows): {neg}")

    zero_days = (df["Total followers"] == 0).sum()
    if zero_days > 0:
        report["warnings"].append(f"Days with zero new followers: {zero_days}")


def print_report(report):
    status = "PASSED" if report["passed"] else "FAILED"
    print(f"\n{'='*60}")
    print(f"  DATA VALIDATION REPORT — {status}")
    print(f"{'='*60}")
    print(f"\n  Summary:")
    for k, v in report["summary"].items():
        print(f"    {k}: {v}")
    if report["errors"]:
        print(f"\n  Errors ({len(report['errors'])}):")
        for e in report["errors"]:
            print(f"    ✗ {e}")
    if report["warnings"]:
        print(f"\n  Warnings ({len(report['warnings'])}):")
        for w in report["warnings"]:
            print(f"    ⚠ {w}")
    if not report["errors"] and not report["warnings"]:
        print(f"\n  ✓ All checks passed with no issues.")
    print(f"\n{'='*60}\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python data_validation.py <path_to_csv> [<path_to_csv2> ...]")
        sys.exit(1)
    all_passed = True
    for csv_file in sys.argv[1:]:
        print(f"\nValidating: {csv_file}")
        result = validate_csv(csv_file)
        print_report(result)
        if not result["passed"]:
            all_passed = False
    sys.exit(0 if all_passed else 1)