"""
visualizations.py — Generate analysis charts and save to figures/ directory.

Produces:
    1. impressions_trend.png     — Daily impressions with 7-day rolling average
    2. engagement_rate_trend.png — Engagement rate trend over time
    3. monthly_summary.png       — Monthly bar chart (impressions + engagement)
    4. day_of_week.png           — Day-of-week performance heatmap
    5. engagement_composition.png — Stacked bar of clicks/reactions/comments/reposts
    6. reach_analysis.png        — Total vs unique impressions
    7. top_days.png              — Horizontal bar chart of top performing days
"""

import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np


# --- Style configuration ---
COLORS = {
    "primary": "#8b5cf6",
    "secondary": "#6366f1",
    "green": "#22c55e",
    "orange": "#f97316",
    "pink": "#ec4899",
    "cyan": "#06b6d4",
    "bg": "#0f1117",
    "surface": "#1a1d29",
    "text": "#e0e0e0",
    "grid": "#2a2d3a",
}

plt.rcParams.update({
    "figure.facecolor": COLORS["bg"],
    "axes.facecolor": COLORS["surface"],
    "axes.edgecolor": COLORS["grid"],
    "axes.labelcolor": COLORS["text"],
    "text.color": COLORS["text"],
    "xtick.color": COLORS["text"],
    "ytick.color": COLORS["text"],
    "grid.color": COLORS["grid"],
    "grid.alpha": 0.3,
    "font.family": "sans-serif",
    "font.size": 10,
})


def _save(fig, output_dir, filename):
    path = os.path.join(output_dir, filename)
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor=COLORS["bg"])
    plt.close(fig)
    print(f"  [SAVED] {path}")


def plot_impressions_trend(df: pd.DataFrame, output_dir: str):
    """Daily impressions with 7-day rolling average."""
    fig, ax = plt.subplots(figsize=(14, 5))

    ax.fill_between(df["Date"], df["Impressions (total)"], alpha=0.15, color=COLORS["primary"])
    ax.plot(df["Date"], df["Impressions (total)"], alpha=0.3, linewidth=0.5, color=COLORS["primary"])

    rolling = df["Impressions (total)"].rolling(7).mean()
    ax.plot(df["Date"], rolling, linewidth=2, color=COLORS["primary"], label="7-day avg")

    ax.set_title("Daily Impressions — 7-Day Rolling Average", fontsize=14, fontweight="bold", pad=12)
    ax.set_ylabel("Impressions")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
    ax.legend(framealpha=0.3)
    ax.grid(True, alpha=0.2)
    fig.autofmt_xdate()

    _save(fig, output_dir, "impressions_trend.png")


def plot_engagement_trend(df: pd.DataFrame, output_dir: str):
    """Engagement rate trend with 7-day rolling average."""
    fig, ax = plt.subplots(figsize=(14, 5))

    rate = df["Engagement rate (total)"] * 100
    rolling = rate.rolling(7).mean()

    ax.fill_between(df["Date"], rate, alpha=0.1, color=COLORS["green"])
    ax.plot(df["Date"], rate, alpha=0.2, linewidth=0.5, color=COLORS["green"])
    ax.plot(df["Date"], rolling, linewidth=2, color=COLORS["green"], label="7-day avg")

    ax.set_title("Engagement Rate Trend — 7-Day Rolling Average", fontsize=14, fontweight="bold", pad=12)
    ax.set_ylabel("Engagement Rate (%)")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
    ax.legend(framealpha=0.3)
    ax.grid(True, alpha=0.2)
    fig.autofmt_xdate()

    _save(fig, output_dir, "engagement_rate_trend.png")


def plot_monthly_summary(df: pd.DataFrame, output_dir: str):
    """Monthly impressions and engagement as grouped bars."""
    df_m = df.set_index("Date").resample("ME").agg({
        "Impressions (total)": "sum",
        "Total Engagement": "sum",
        "Engagement rate (total)": "mean",
    }).reset_index()
    df_m["month_label"] = df_m["Date"].dt.strftime("%b\n%y")

    fig, ax1 = plt.subplots(figsize=(14, 6))
    x = np.arange(len(df_m))
    w = 0.35

    bars1 = ax1.bar(x - w/2, df_m["Impressions (total)"], w, color=COLORS["primary"], alpha=0.8, label="Impressions")
    bars2 = ax1.bar(x + w/2, df_m["Total Engagement"], w, color=COLORS["secondary"], alpha=0.8, label="Engagement")

    ax2 = ax1.twinx()
    ax2.plot(x, df_m["Engagement rate (total)"] * 100, color=COLORS["green"], linewidth=2, marker="o", markersize=5, label="Eng. Rate %")
    ax2.set_ylabel("Engagement Rate (%)", color=COLORS["green"])
    ax2.tick_params(axis="y", labelcolor=COLORS["green"])

    ax1.set_xticks(x)
    ax1.set_xticklabels(df_m["month_label"])
    ax1.set_ylabel("Count")
    ax1.set_title("Monthly Performance Breakdown", fontsize=14, fontweight="bold", pad=12)

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left", framealpha=0.3)
    ax1.grid(True, alpha=0.15, axis="y")

    _save(fig, output_dir, "monthly_summary.png")


def plot_day_of_week(df: pd.DataFrame, output_dir: str):
    """Day-of-week average performance."""
    df_temp = df.copy()
    df_temp["DayOfWeek"] = df_temp["Date"].dt.day_name()
    dow_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    dow = df_temp.groupby("DayOfWeek").agg({
        "Impressions (total)": "mean",
        "Total Engagement": "mean",
    }).reindex(dow_order)

    fig, ax = plt.subplots(figsize=(10, 5))
    x = np.arange(len(dow_order))
    w = 0.35

    ax.bar(x - w/2, dow["Impressions (total)"], w, color=COLORS["primary"], alpha=0.8, label="Avg Impressions")
    ax.bar(x + w/2, dow["Total Engagement"], w, color=COLORS["secondary"], alpha=0.8, label="Avg Engagement")

    ax.set_xticks(x)
    ax.set_xticklabels([d[:3] for d in dow_order])
    ax.set_title("Average Performance by Day of Week", fontsize=14, fontweight="bold", pad=12)
    ax.legend(framealpha=0.3)
    ax.grid(True, alpha=0.15, axis="y")

    _save(fig, output_dir, "day_of_week.png")


def plot_engagement_composition(df: pd.DataFrame, output_dir: str):
    """Monthly stacked bar chart of engagement components."""
    df_m = df.set_index("Date").resample("ME").agg({
        "Clicks (total)": "sum",
        "Reactions (total)": "sum",
        "Comments (total)": "sum",
        "Reposts (total)": "sum",
    }).reset_index()
    df_m["month_label"] = df_m["Date"].dt.strftime("%b\n%y")

    fig, ax = plt.subplots(figsize=(14, 5))
    x = np.arange(len(df_m))

    bottom = np.zeros(len(df_m))
    for col, color, label in [
        ("Clicks (total)", COLORS["primary"], "Clicks"),
        ("Reactions (total)", COLORS["secondary"], "Reactions"),
        ("Comments (total)", COLORS["green"], "Comments"),
        ("Reposts (total)", COLORS["orange"], "Reposts"),
    ]:
        vals = df_m[col].values
        ax.bar(x, vals, bottom=bottom, color=color, alpha=0.85, label=label)
        bottom += vals

    ax.set_xticks(x)
    ax.set_xticklabels(df_m["month_label"])
    ax.set_title("Engagement Composition by Month", fontsize=14, fontweight="bold", pad=12)
    ax.set_ylabel("Count")
    ax.legend(framealpha=0.3)
    ax.grid(True, alpha=0.15, axis="y")

    _save(fig, output_dir, "engagement_composition.png")


def plot_reach_analysis(df: pd.DataFrame, output_dir: str):
    """Total vs unique impressions by month."""
    df_m = df.set_index("Date").resample("ME").agg({
        "Impressions (total)": "sum",
        "Unique impressions (organic)": "sum",
    }).reset_index()
    df_m["month_label"] = df_m["Date"].dt.strftime("%b\n%y")

    fig, ax = plt.subplots(figsize=(14, 5))
    x = np.arange(len(df_m))
    w = 0.35

    ax.bar(x - w/2, df_m["Impressions (total)"], w, color=COLORS["primary"], alpha=0.5, label="Total Impressions")
    ax.bar(x + w/2, df_m["Unique impressions (organic)"], w, color=COLORS["pink"], alpha=0.8, label="Unique Impressions")

    ax.set_xticks(x)
    ax.set_xticklabels(df_m["month_label"])
    ax.set_title("Reach: Total vs Unique Impressions", fontsize=14, fontweight="bold", pad=12)
    ax.set_ylabel("Impressions")
    ax.legend(framealpha=0.3)
    ax.grid(True, alpha=0.15, axis="y")

    _save(fig, output_dir, "reach_analysis.png")


def plot_top_days(df: pd.DataFrame, output_dir: str, n: int = 10):
    """Horizontal bar chart of top performing days."""
    top = df.nlargest(n, "Impressions (total)").sort_values("Impressions (total)")

    fig, ax = plt.subplots(figsize=(10, 6))
    labels = top["Date"].dt.strftime("%b %d, %Y")
    y = np.arange(len(top))

    ax.barh(y, top["Impressions (total)"], color=COLORS["primary"], alpha=0.8)

    for i, (imp, eng) in enumerate(zip(top["Impressions (total)"], top["Engagement rate (total)"])):
        ax.text(imp + 30, i, f"{eng*100:.1f}%", va="center", fontsize=9, color=COLORS["green"])

    ax.set_yticks(y)
    ax.set_yticklabels(labels)
    ax.set_xlabel("Impressions")
    ax.set_title(f"Top {n} Performing Days (with Engagement Rate)", fontsize=14, fontweight="bold", pad=12)
    ax.grid(True, alpha=0.15, axis="x")

    _save(fig, output_dir, "top_days.png")


def generate_all_charts(csv_path: str, output_dir: str = "figures"):
    """Generate all visualization charts."""
    os.makedirs(output_dir, exist_ok=True)

    df = pd.read_csv(csv_path)
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values("Date").reset_index(drop=True)
    if "Total Engagement" not in df.columns:
        df["Total Engagement"] = (
            df["Clicks (total)"] + df["Reactions (total)"]
            + df["Comments (total)"] + df["Reposts (total)"]
        )

    print(f"\nGenerating charts in: {output_dir}/")
    print("-" * 40)

    plot_impressions_trend(df, output_dir)
    plot_engagement_trend(df, output_dir)
    plot_monthly_summary(df, output_dir)
    plot_day_of_week(df, output_dir)
    plot_engagement_composition(df, output_dir)
    plot_reach_analysis(df, output_dir)
    plot_top_days(df, output_dir)

    print("-" * 40)
    print(f"Done! {7} charts generated.\n")


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python visualizations.py <path_to_csv> [output_dir]")
        sys.exit(1)

    csv_file = sys.argv[1]
    out_dir = sys.argv[2] if len(sys.argv) > 2 else "figures"
    generate_all_charts(csv_file, out_dir)