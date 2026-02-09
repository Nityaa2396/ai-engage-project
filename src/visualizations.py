"""
visualizations.py — Generate analysis charts and save to figures/ directory.

Produces:
    1. impressions_trend.png          — Daily impressions with 7-day rolling average
    2. engagement_rate_trend.png      — Engagement rate trend over time
    3. monthly_summary.png            — Monthly bar chart (impressions + engagement)
    4. day_of_week.png                — Day-of-week performance
    5. engagement_composition.png     — Stacked bar of clicks/reactions/comments/reposts
    6. reach_analysis.png             — Total vs unique impressions
    7. top_days.png                   — Horizontal bar chart of top performing days
    8. follower_growth.png            — Cumulative follower growth over time
    9. follower_monthly.png           — Monthly new followers bar chart
    10. follower_vs_engagement.png    — Follower growth vs content performance correlation
"""

import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")
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


def plot_impressions_trend(df, output_dir):
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


def plot_engagement_trend(df, output_dir):
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


def plot_monthly_summary(df, output_dir):
    df_m = df.set_index("Date").resample("ME").agg({
        "Impressions (total)": "sum", "Total Engagement": "sum", "Engagement rate (total)": "mean",
    }).reset_index()
    df_m["month_label"] = df_m["Date"].dt.strftime("%b\n%y")
    fig, ax1 = plt.subplots(figsize=(14, 6))
    x = np.arange(len(df_m))
    w = 0.35
    ax1.bar(x - w/2, df_m["Impressions (total)"], w, color=COLORS["primary"], alpha=0.8, label="Impressions")
    ax1.bar(x + w/2, df_m["Total Engagement"], w, color=COLORS["secondary"], alpha=0.8, label="Engagement")
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


def plot_day_of_week(df, output_dir):
    df_temp = df.copy()
    df_temp["DayOfWeek"] = df_temp["Date"].dt.day_name()
    dow_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    dow = df_temp.groupby("DayOfWeek").agg({"Impressions (total)": "mean", "Total Engagement": "mean"}).reindex(dow_order)
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


def plot_engagement_composition(df, output_dir):
    df_m = df.set_index("Date").resample("ME").agg({
        "Clicks (total)": "sum", "Reactions (total)": "sum", "Comments (total)": "sum", "Reposts (total)": "sum",
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


def plot_reach_analysis(df, output_dir):
    df_m = df.set_index("Date").resample("ME").agg({
        "Impressions (total)": "sum", "Unique impressions (organic)": "sum",
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


def plot_top_days(df, output_dir, n=10):
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


# ---------------------------------------------------------------------------
# FOLLOWER CHARTS
# ---------------------------------------------------------------------------

def plot_follower_growth(df_f, output_dir):
    """Cumulative follower growth over time with daily new followers."""
    fig, ax1 = plt.subplots(figsize=(14, 5))

    # Daily new followers as bars
    ax1.bar(df_f["Date"], df_f["Total followers"], alpha=0.3, color=COLORS["cyan"], width=1.0, label="Daily new followers")

    # 7-day rolling average
    rolling = df_f["Total followers"].rolling(7).mean()
    ax1.plot(df_f["Date"], rolling, linewidth=2, color=COLORS["cyan"], label="7-day avg")

    # Cumulative on secondary axis
    ax2 = ax1.twinx()
    ax2.plot(df_f["Date"], df_f["Cumulative Followers"], linewidth=2.5, color=COLORS["pink"], label="Cumulative followers")
    ax2.set_ylabel("Cumulative Followers", color=COLORS["pink"])
    ax2.tick_params(axis="y", labelcolor=COLORS["pink"])

    ax1.set_title("Follower Growth — Daily New & Cumulative", fontsize=14, fontweight="bold", pad=12)
    ax1.set_ylabel("New Followers / Day")
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=2))

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left", framealpha=0.3)
    ax1.grid(True, alpha=0.2)
    fig.autofmt_xdate()
    _save(fig, output_dir, "follower_growth.png")


def plot_follower_monthly(df_f, output_dir):
    """Monthly new followers bar chart."""
    df_m = df_f.set_index("Date").resample("ME")["Total followers"].sum().reset_index()
    df_m["month_label"] = df_m["Date"].dt.strftime("%b\n%y")

    fig, ax = plt.subplots(figsize=(12, 5))
    x = np.arange(len(df_m))
    bars = ax.bar(x, df_m["Total followers"], color=COLORS["cyan"], alpha=0.85)

    # Add value labels on bars
    for i, v in enumerate(df_m["Total followers"]):
        ax.text(i, v + 3, str(v), ha="center", fontsize=9, color=COLORS["text"])

    ax.set_xticks(x)
    ax.set_xticklabels(df_m["month_label"])
    ax.set_title("Monthly New Followers", fontsize=14, fontweight="bold", pad=12)
    ax.set_ylabel("New Followers")
    ax.grid(True, alpha=0.15, axis="y")
    _save(fig, output_dir, "follower_monthly.png")


def plot_follower_vs_engagement(df_content, df_followers, output_dir):
    """Monthly follower growth vs impressions and engagement."""
    # Merge on overlapping dates, then aggregate monthly
    merged = pd.merge(
        df_content[["Date", "Impressions (total)", "Total Engagement"]],
        df_followers[["Date", "Total followers"]],
        on="Date", how="inner"
    )
    if len(merged) == 0:
        print("  [SKIP] follower_vs_engagement.png — no overlapping dates")
        return

    monthly = merged.set_index("Date").resample("ME").agg({
        "Impressions (total)": "sum",
        "Total Engagement": "sum",
        "Total followers": "sum",
    }).reset_index()
    monthly["month_label"] = monthly["Date"].dt.strftime("%b\n%y")

    fig, ax1 = plt.subplots(figsize=(14, 6))
    x = np.arange(len(monthly))
    w = 0.25

    ax1.bar(x - w, monthly["Impressions (total)"] / 100, w, color=COLORS["primary"], alpha=0.7, label="Impressions (÷100)")
    ax1.bar(x, monthly["Total Engagement"], w, color=COLORS["secondary"], alpha=0.7, label="Engagement")

    ax2 = ax1.twinx()
    ax2.bar(x + w, monthly["Total followers"], w, color=COLORS["cyan"], alpha=0.9, label="New Followers")
    ax2.set_ylabel("New Followers", color=COLORS["cyan"])
    ax2.tick_params(axis="y", labelcolor=COLORS["cyan"])

    ax1.set_xticks(x)
    ax1.set_xticklabels(monthly["month_label"])
    ax1.set_ylabel("Impressions (÷100) / Engagement")
    ax1.set_title("Content Performance vs Follower Growth", fontsize=14, fontweight="bold", pad=12)

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left", framealpha=0.3)
    ax1.grid(True, alpha=0.15, axis="y")
    _save(fig, output_dir, "follower_vs_engagement.png")


# ---------------------------------------------------------------------------
# GENERATE ALL
# ---------------------------------------------------------------------------

def generate_all_charts(content_csv: str, output_dir: str = "figures", followers_csv: str = None):
    """Generate all visualization charts."""
    os.makedirs(output_dir, exist_ok=True)

    df = pd.read_csv(content_csv)
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values("Date").reset_index(drop=True)
    if "Total Engagement" not in df.columns:
        df["Total Engagement"] = (
            df["Clicks (total)"] + df["Reactions (total)"]
            + df["Comments (total)"] + df["Reposts (total)"]
        )

    chart_count = 7
    print(f"\nGenerating charts in: {output_dir}/")
    print("-" * 40)

    plot_impressions_trend(df, output_dir)
    plot_engagement_trend(df, output_dir)
    plot_monthly_summary(df, output_dir)
    plot_day_of_week(df, output_dir)
    plot_engagement_composition(df, output_dir)
    plot_reach_analysis(df, output_dir)
    plot_top_days(df, output_dir)

    # Follower charts
    if followers_csv and os.path.exists(followers_csv):
        df_f = pd.read_csv(followers_csv)
        df_f["Date"] = pd.to_datetime(df_f["Date"])
        df_f = df_f.sort_values("Date").reset_index(drop=True)
        if "Cumulative Followers" not in df_f.columns:
            df_f["Cumulative Followers"] = df_f["Total followers"].cumsum()

        plot_follower_growth(df_f, output_dir)
        plot_follower_monthly(df_f, output_dir)
        plot_follower_vs_engagement(df, df_f, output_dir)
        chart_count += 3

    print("-" * 40)
    print(f"Done! {chart_count} charts generated.\n")


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python visualizations.py <content_csv> [output_dir] [--followers <followers_csv>]")
        print("\nExamples:")
        print("  python visualizations.py data/women_in_ai_usa_clean.csv figures/")
        print("  python visualizations.py data/women_in_ai_usa_clean.csv figures/ --followers data/women_in_ai_usa_followers.csv")
        sys.exit(1)

    content_file = sys.argv[1]
    out_dir = "figures"
    followers_file = None

    args = sys.argv[2:]
    i = 0
    while i < len(args):
        if args[i] == "--followers" and i + 1 < len(args):
            followers_file = args[i + 1]
            i += 2
        elif not args[i].startswith("--"):
            out_dir = args[i]
            i += 1
        else:
            i += 1

    generate_all_charts(content_file, out_dir, followers_file)