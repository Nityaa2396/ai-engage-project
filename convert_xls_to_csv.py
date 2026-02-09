"""
Convert XLS to CSV - Women in AI USA LinkedIn Analytics
Handles encoding issues in .xls files by using LibreOffice fallback.
"""

import os
import sys
import subprocess
import pandas as pd


def convert_xls_to_csv(input_path: str, output_path: str = None) -> str:
    """
    Convert an .xls file to a clean .csv file.

    Attempts pandas/xlrd first, falls back to LibreOffice for encoding issues.

    Args:
        input_path: Path to the source .xls file.
        output_path: Path for the output .csv file. Defaults to data/women_in_ai_usa_clean.csv.

    Returns:
        Path to the generated CSV file.
    """
    if output_path is None:
        output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, "women_in_ai_usa_clean.csv")

    # --- Attempt 1: Direct pandas read ---
    try:
        df = pd.read_excel(input_path, engine="xlrd")
        print("[INFO] Successfully read with xlrd engine.")
    except Exception as e:
        print(f"[WARN] xlrd failed ({e}). Falling back to LibreOffice conversion.")
        df = _convert_via_libreoffice(input_path)

    # --- Clean the data ---
    df = _clean_dataframe(df)

    # --- Save ---
    df.to_csv(output_path, index=False)
    print(f"[OK] CSV saved to: {output_path}")
    print(f"     Rows: {len(df)} | Columns: {len(df.columns)}")
    return output_path


def _convert_via_libreoffice(input_path: str) -> pd.DataFrame:
    """Use LibreOffice headless mode to convert XLS -> CSV, then read with pandas."""
    tmp_dir = "/tmp/xls_convert"
    os.makedirs(tmp_dir, exist_ok=True)

    result = subprocess.run(
        ["libreoffice", "--headless", "--convert-to", "csv", input_path, "--outdir", tmp_dir],
        capture_output=True, text=True, timeout=60,
    )

    if result.returncode != 0:
        raise RuntimeError(f"LibreOffice conversion failed: {result.stderr}")

    basename = os.path.splitext(os.path.basename(input_path))[0]
    csv_path = os.path.join(tmp_dir, f"{basename}.csv")

    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Expected output not found: {csv_path}")

    # The first row is a description line — skip it
    df = pd.read_csv(csv_path, skiprows=1)
    os.remove(csv_path)
    return df


def _clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Validate and clean the LinkedIn analytics dataframe.

    - Standardize date format to YYYY-MM-DD
    - Add computed 'Total Engagement' column
    - Sort by date ascending
    """
    # Standardize the Date column
    df["Date"] = pd.to_datetime(df["Date"], format="mixed", dayfirst=False)
    df = df.sort_values("Date").reset_index(drop=True)
    df["Date"] = df["Date"].dt.strftime("%Y-%m-%d")

    # Add computed engagement column
    df["Total Engagement"] = (
        df["Clicks (total)"]
        + df["Reactions (total)"]
        + df["Comments (total)"]
        + df["Reposts (total)"]
    )

    # Report data quality
    null_count = df.isnull().sum().sum()
    neg_cols = ["Reactions (total)", "Comments (total)", "Reposts (total)"]
    neg_count = sum((df[c] < 0).sum() for c in neg_cols if c in df.columns)

    print(f"[VALIDATION] Null values: {null_count}")
    print(f"[VALIDATION] Negative values (LinkedIn corrections): {neg_count}")
    print(f"[VALIDATION] Date range: {df['Date'].iloc[0]} to {df['Date'].iloc[-1]}")

    return df


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python convert_xls_to_csv.py <path_to_xls_file> [output_csv_path]")
        sys.exit(1)

    xls_path = sys.argv[1]
    csv_path = sys.argv[2] if len(sys.argv) > 2 else None
    convert_xls_to_csv(xls_path, csv_path)