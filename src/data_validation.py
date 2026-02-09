"""
data_validation.py — Data quality checks for LinkedIn analytics CSV.

Validates structure, types, missing values, date consistency, and value ranges.
"""

import pandas as pd
import sys


REQUIRED_COLUMNS = [
    "Date",
    "Impressions (organic)",
    "Impressions (sponsored)",
    "Impressions (total)",
    "Unique impressions (organic)",
    "Clicks (organic)",
    "Clicks (sponsored)",
    "Clicks (total)",
    "Reactions (organic)",
    "Reactions (sponsored)",
    "Reactions (total)",
    "Comments (organic)",
    "Comments (sponsored)",
    "Comments (total)",
    "Reposts (organic)",
    "Reposts (sponsored)",
    "Reposts (total)",
    "Engagement rate (organic)",
    "Engagement rate (sponsored)",
    "Engagement rate (total)",
]


def validate_csv(csv_path: str) -> dict:
    """
    Run all validation checks on the CSV file.

    Returns:
        dict with keys: 'passed', 'warnings', 'errors', 'summary'
    """
    report = {"passed": True, "warnings": [], "errors": [], "summary": {}}

    # --- Load ---
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        report["passed"] = False
        report["errors"].append(f"Cannot read CSV: {e}")
        return report

    report["summary"]["rows"] = len(df)
    report["summary"]["columns"] = len(df.columns)

    # --- 1. Column check ---
    missing_cols = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing_cols:
        report["passed"] = False
        report["errors"].append(f"Missing columns: {missing_cols}")

    extra_cols = [c for c in df.columns if c not in REQUIRED_COLUMNS and c != "Total Engagement"]
    if extra_cols:
        report["warnings"].append(f"Extra columns found (OK): {extra_cols}")

    # --- 2. Null values ---
    null_counts = df.isnull().sum()
    total_nulls = null_counts.sum()
    if total_nulls > 0:
        report["passed"] = False
        cols_with_nulls = null_counts[null_counts > 0].to_dict()
        report["errors"].append(f"Null values found: {cols_with_nulls}")
    else:
        report["summary"]["null_values"] = 0

    # --- 3. Date format ---
    try:
        dates = pd.to_datetime(df["Date"], format="mixed")
        report["summary"]["date_range"] = f"{dates.min().date()} to {dates.max().date()}"
        report["summary"]["total_days"] = len(dates)

        # Check for duplicates
        dupes = dates.duplicated().sum()
        if dupes > 0:
            report["warnings"].append(f"Duplicate dates found: {dupes}")

        # Check for gaps
        date_range = pd.date_range(dates.min(), dates.max())
        missing_dates = set(date_range) - set(dates)
        if missing_dates:
            report["warnings"].append(f"Missing dates in range: {len(missing_dates)}")
    except Exception as e:
        report["passed"] = False
        report["errors"].append(f"Date parsing error: {e}")

    # --- 4. Numeric consistency ---
    numeric_cols = [c for c in df.columns if c != "Date"]
    for col in numeric_cols:
        if col in df.columns:
            try:
                pd.to_numeric(df[col])
            except (ValueError, TypeError):
                report["errors"].append(f"Non-numeric values in column: {col}")
                report["passed"] = False

    # --- 5. Negative value check ---
    count_cols = ["Impressions (total)", "Clicks (total)", "Reactions (total)",
                  "Comments (total)", "Reposts (total)"]
    negatives = {}
    for col in count_cols:
        if col in df.columns:
            neg = (df[col] < 0).sum()
            if neg > 0:
                negatives[col] = int(neg)
    if negatives:
        report["warnings"].append(
            f"Negative values detected (LinkedIn data corrections): {negatives}"
        )

    # --- 6. Engagement rate sanity ---
    if "Engagement rate (total)" in df.columns:
        eng = df["Engagement rate (total)"]
        out_of_range = ((eng < 0) | (eng > 1)).sum()
        if out_of_range > 0:
            report["warnings"].append(
                f"Engagement rates outside [0, 1]: {out_of_range} rows"
            )

    # --- 7. Sponsored column check ---
    sponsored_cols = [c for c in df.columns if "sponsored" in c.lower()]
    all_zero = all(df[c].sum() == 0 for c in sponsored_cols if c in df.columns)
    report["summary"]["has_sponsored_data"] = not all_zero

    return report


def print_report(report: dict) -> None:
    """Pretty-print the validation report."""
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
        print("Usage: python data_validation.py <path_to_csv>")
        sys.exit(1)
    result = validate_csv(sys.argv[1])
    print_report(result)
    sys.exit(0 if result["passed"] else 1)