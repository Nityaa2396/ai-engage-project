"""
Convert XLS to CSV - Women in AI USA LinkedIn Analytics
Handles both content analytics and follower metrics exports.
Uses LibreOffice fallback for encoding issues.
"""

import os
import sys
import subprocess
import pandas as pd


def convert_xls_to_csv(input_path: str, output_path: str = None, data_type: str = "auto") -> str:
    """
    Convert a LinkedIn .xls export to a clean .csv file.

    Args:
        input_path: Path to the source .xls file.
        output_path: Path for the output .csv file.
        data_type: "content", "followers", or "auto" (detect from columns).

    Returns:
        Path to the generated CSV file.
    """
    if output_path is None:
        output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
        os.makedirs(output_dir, exist_ok=True)

    # --- Read the XLS ---
    try:
        df = pd.read_excel(input_path, engine="xlrd")
        print(f"[INFO] Successfully read with xlrd engine.")
    except Exception as e:
        print(f"[WARN] xlrd failed ({e}). Falling back to LibreOffice conversion.")
        df = _convert_via_libreoffice(input_path)

    # --- Auto-detect data type ---
    if data_type == "auto":
        if "Total followers" in df.columns:
            data_type = "followers"
        elif "Impressions (total)" in df.columns:
            data_type = "content"
        else:
            data_type = "unknown"
        print(f"[INFO] Auto-detected data type: {data_type}")

    # --- Clean based on type ---
    if data_type == "followers":
        df = _clean_followers(df)
        if output_path is None:
            output_path = os.path.join(output_dir, "women_in_ai_usa_followers.csv")
    elif data_type == "content":
        df = _clean_content(df)
        if output_path is None:
            output_path = os.path.join(output_dir, "women_in_ai_usa_clean.csv")
    else:
        df["Date"] = pd.to_datetime(df["Date"], format="mixed", dayfirst=False)
        df = df.sort_values("Date").reset_index(drop=True)
        df["Date"] = df["Date"].dt.strftime("%Y-%m-%d")
        if output_path is None:
            output_path = os.path.join(output_dir, "women_in_ai_usa_data.csv")

    # --- Save ---
    df.to_csv(output_path, index=False)
    print(f"[OK] CSV saved to: {output_path}")
    print(f"     Rows: {len(df)} | Columns: {len(df.columns)} | Type: {data_type}")
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

    df = pd.read_csv(csv_path, skiprows=1)
    os.remove(csv_path)
    return df


def _clean_content(df: pd.DataFrame) -> pd.DataFrame:
    """Clean the LinkedIn content analytics dataframe."""
    df["Date"] = pd.to_datetime(df["Date"], format="mixed", dayfirst=False)
    df = df.sort_values("Date").reset_index(drop=True)
    df["Date"] = df["Date"].dt.strftime("%Y-%m-%d")

    df["Total Engagement"] = (
        df["Clicks (total)"]
        + df["Reactions (total)"]
        + df["Comments (total)"]
        + df["Reposts (total)"]
    )

    null_count = df.isnull().sum().sum()
    neg_cols = ["Reactions (total)", "Comments (total)", "Reposts (total)"]
    neg_count = sum((df[c] < 0).sum() for c in neg_cols if c in df.columns)

    print(f"[VALIDATION] Null values: {null_count}")
    print(f"[VALIDATION] Negative values (LinkedIn corrections): {neg_count}")
    print(f"[VALIDATION] Date range: {df['Date'].iloc[0]} to {df['Date'].iloc[-1]}")
    return df


def _clean_followers(df: pd.DataFrame) -> pd.DataFrame:
    """Clean the LinkedIn followers dataframe and add cumulative totals."""
    df["Date"] = pd.to_datetime(df["Date"], format="mixed", dayfirst=False)
    df = df.sort_values("Date").reset_index(drop=True)

    # Add cumulative followers
    df["Cumulative Followers"] = df["Total followers"].cumsum()

    # Add 7-day rolling average
    df["Followers 7d Avg"] = df["Total followers"].rolling(7, min_periods=1).mean().round(2)

    df["Date"] = df["Date"].dt.strftime("%Y-%m-%d")

    null_count = df.isnull().sum().sum()
    total_gained = df["Total followers"].sum()
    print(f"[VALIDATION] Null values: {null_count}")
    print(f"[VALIDATION] Total new followers: {total_gained}")
    print(f"[VALIDATION] All organic: {df['Sponsored followers'].sum() == 0}")
    print(f"[VALIDATION] Date range: {df['Date'].iloc[0]} to {df['Date'].iloc[-1]}")
    return df


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python convert_xls_to_csv.py <path_to_xls> [output_csv] [content|followers|auto]")
        print("\nExamples:")
        print("  python convert_xls_to_csv.py data/content_export.xls")
        print("  python convert_xls_to_csv.py data/followers_export.xls data/followers.csv followers")
        sys.exit(1)

    xls_path = sys.argv[1]
    csv_path = sys.argv[2] if len(sys.argv) > 2 else None
    dtype = sys.argv[3] if len(sys.argv) > 3 else "auto"
    convert_xls_to_csv(xls_path, csv_path, dtype)