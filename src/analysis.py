"""
analysis.py — Core metric calculations for LinkedIn social media analytics.

Metrics tracked:
    1. Followers — Real follower growth from LinkedIn followers export
    2. Engagement Rate = (Clicks + Reactions + Comments + Reposts) / Impressions
    3. Post Frequency = Days with meaningful engagement activity
    4. Reach = Total and unique impressions over time

All functions accept pandas DataFrames with the standard LinkedIn export schema.
"""

import pandas as pd
import numpy as np
import json
import os


def load_data(csv_path: str) -> pd.DataFrame:
    """Load and prepare the clean content CSV data."""
    df = pd.read_csv(csv_path)
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values("Date").reset_index(drop=True)

    if "Total Engagement" not in df.columns:
        df["Total Engagement"] = (
            df["Clicks (total)"]
            + df["Reactions (total)"]
            + df["Comments (total)"]
            + df["Reposts (total)"]
        )
    return df


def load_followers(csv_path: str) -> pd.DataFrame:
    """Load and prepare the followers CSV data."""
    df = pd.read_csv(csv_path)
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values("Date").reset_index(drop=True)

    if "Cumulative Followers" not in df.columns:
        df["Cumulative Followers"] = df["Total followers"].cumsum()
    if "Followers 7d Avg" not in df.columns:
        df["Followers 7d Avg"] = df["Total followers"].rolling(7, min_periods=1).mean().round(2)
    return df


# ---------------------------------------------------------------------------
# 1. FOLLOWERS (REAL DATA)
# ---------------------------------------------------------------------------

def calculate_followers(df_followers: pd.DataFrame) -> dict:
    """
    Analyze real follower growth data from LinkedIn export.

    Returns:
        dict with total gained, monthly breakdown, growth rate, best/worst months
    """
    total_gained = int(df_followers["Total followers"].sum())
    organic = int(df_followers["Organic followers"].sum())
    sponsored = int(df_followers["Sponsored followers"].sum())

    # Monthly breakdown
    df_m = df_followers.set_index("Date").resample("ME").agg({
        "Total followers": "sum",
        "Organic followers": "sum",
        "Cumulative Followers": "last",
    }).reset_index()
    df_m["month"] = df_m["Date"].dt.strftime("%Y-%m")
    df_m["growth_pct"] = df_m["Total followers"].pct_change().round(3) * 100

    # Best and worst months
    best_month = df_m.loc[df_m["Total followers"].idxmax()]
    worst_month = df_m.loc[df_m["Total followers"].idxmin()]

    # Daily stats
    avg_daily = round(df_followers["Total followers"].mean(), 2)
    max_daily = int(df_followers["Total followers"].max())
    max_daily_date = df_followers.loc[df_followers["Total followers"].idxmax(), "Date"].strftime("%Y-%m-%d")

    # Days with zero new followers
    zero_days = int((df_followers["Total followers"] == 0).sum())

    # Growth trend: compare last 3 months vs first 3 months
    months = df_m["Total followers"].tolist()
    if len(months) >= 6:
        first_3 = np.mean(months[:3])
        last_3 = np.mean(months[-3:])
        trend_pct = round(((last_3 - first_3) / first_3) * 100, 1) if first_3 > 0 else 0
    else:
        trend_pct = 0

    # Day-of-week follower patterns
    df_temp = df_followers.copy()
    df_temp["DayOfWeek"] = df_temp["Date"].dt.day_name()
    dow_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    dow = df_temp.groupby("DayOfWeek")["Total followers"].mean().reindex(dow_order).round(2)

    return {
        "total_gained": total_gained,
        "organic": organic,
        "sponsored": sponsored,
        "all_organic": sponsored == 0,
        "avg_daily_new": avg_daily,
        "max_daily_new": max_daily,
        "max_daily_date": max_daily_date,
        "zero_follower_days": zero_days,
        "date_range": f"{df_followers['Date'].min().strftime('%Y-%m-%d')} to {df_followers['Date'].max().strftime('%Y-%m-%d')}",
        "total_days": len(df_followers),
        "cumulative_at_end": int(df_m["Cumulative Followers"].iloc[-1]),
        "growth_trend_pct": trend_pct,
        "best_month": {"month": best_month["month"], "gained": int(best_month["Total followers"])},
        "worst_month": {"month": worst_month["month"], "gained": int(worst_month["Total followers"])},
        "monthly": df_m[["month", "Total followers", "Cumulative Followers", "growth_pct"]].to_dict(orient="records"),
        "day_of_week_avg": dow.to_dict(),
    }


# ---------------------------------------------------------------------------
# 2. ENGAGEMENT RATE
# ---------------------------------------------------------------------------

def calculate_engagement_rate(df: pd.DataFrame) -> dict:
    """
    Engagement Rate = (Clicks + Reactions + Comments + Reposts) / Impressions.

    Returns:
        dict with overall, daily_avg, monthly, weekly_trend, by_component
    """
    total_eng = df["Total Engagement"].sum()
    total_imp = df["Impressions (total)"].sum()
    overall_rate = total_eng / total_imp if total_imp > 0 else 0

    daily_avg = df["Engagement rate (total)"].mean()

    # Monthly breakdown
    df_m = df.set_index("Date")
    monthly = df_m.resample("ME").agg({
        "Impressions (total)": "sum",
        "Clicks (total)": "sum",
        "Reactions (total)": "sum",
        "Comments (total)": "sum",
        "Reposts (total)": "sum",
        "Total Engagement": "sum",
        "Engagement rate (total)": "mean",
    })
    monthly["calculated_rate"] = monthly["Total Engagement"] / monthly["Impressions (total)"]
    monthly = monthly.reset_index()
    monthly["month"] = monthly["Date"].dt.strftime("%Y-%m")

    # Component breakdown
    components = {
        "clicks": int(df["Clicks (total)"].sum()),
        "reactions": int(df["Reactions (total)"].sum()),
        "comments": int(df["Comments (total)"].sum()),
        "reposts": int(df["Reposts (total)"].sum()),
    }
    components["clicks_pct"] = round(components["clicks"] / total_eng * 100, 1) if total_eng > 0 else 0
    components["reactions_pct"] = round(components["reactions"] / total_eng * 100, 1) if total_eng > 0 else 0
    components["comments_pct"] = round(components["comments"] / total_eng * 100, 1) if total_eng > 0 else 0
    components["reposts_pct"] = round(components["reposts"] / total_eng * 100, 1) if total_eng > 0 else 0

    # 7-day rolling
    rolling = df.set_index("Date")["Engagement rate (total)"].rolling(7).mean().dropna()

    return {
        "overall_rate": round(overall_rate, 4),
        "daily_avg_rate": round(daily_avg, 4),
        "max_daily_rate": round(df["Engagement rate (total)"].max(), 4),
        "min_daily_rate": round(df["Engagement rate (total)"].min(), 4),
        "total_engagement": int(total_eng),
        "components": components,
        "monthly": monthly[["month", "Total Engagement", "Engagement rate (total)", "calculated_rate"]].to_dict(orient="records"),
        "rolling_7d": [{"date": d.strftime("%Y-%m-%d"), "rate": round(v, 4)} for d, v in rolling.items()],
    }


# ---------------------------------------------------------------------------
# 3. POST FREQUENCY
# ---------------------------------------------------------------------------

def calculate_post_frequency(df: pd.DataFrame) -> dict:
    """
    Post frequency approximated by active engagement days and impression spikes.

    Returns:
        dict with active_days, total_days, frequency metrics, spike detection
    """
    total_days = len(df)
    active_days = int((df["Total Engagement"] > 0).sum())

    df_temp = df.copy()
    df_temp["rolling_avg"] = df_temp["Impressions (total)"].rolling(7, min_periods=1).mean()
    df_temp["is_spike"] = df_temp["Impressions (total)"] > (df_temp["rolling_avg"] * 1.5)
    spike_days = int(df_temp["is_spike"].sum())

    # Monthly post frequency proxy
    df_temp["Month"] = df_temp["Date"].dt.to_period("M")
    monthly_activity = df_temp.groupby("Month").agg(
        active_days=("Total Engagement", lambda x: (x > 0).sum()),
        spike_days=("is_spike", "sum"),
        total_days=("Date", "count"),
    ).reset_index()
    monthly_activity["Month"] = monthly_activity["Month"].astype(str)

    # Day-of-week distribution
    df_temp["DayOfWeek"] = df_temp["Date"].dt.day_name()
    dow_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    dow = df_temp.groupby("DayOfWeek").agg(
        avg_impressions=("Impressions (total)", "mean"),
        avg_engagement=("Total Engagement", "mean"),
        avg_rate=("Engagement rate (total)", "mean"),
    ).reindex(dow_order).round(2).reset_index()

    return {
        "total_days": total_days,
        "active_days": active_days,
        "activity_rate_pct": round(active_days / total_days * 100, 1),
        "estimated_spike_days": spike_days,
        "avg_spikes_per_month": round(spike_days / (total_days / 30), 1),
        "monthly_activity": monthly_activity.to_dict(orient="records"),
        "day_of_week_performance": dow.to_dict(orient="records"),
        "best_posting_days": dow.nlargest(3, "avg_impressions")["DayOfWeek"].tolist(),
    }


# ---------------------------------------------------------------------------
# 4. REACH
# ---------------------------------------------------------------------------

def calculate_reach(df: pd.DataFrame) -> dict:
    """
    Reach metrics from impression data.

    Returns:
        dict with total/unique impressions, monthly trend, reach ratio
    """
    total_imp = int(df["Impressions (total)"].sum())
    unique_imp = int(df["Unique impressions (organic)"].sum())

    monthly = (
        df.set_index("Date")
        .resample("ME")
        .agg({
            "Impressions (total)": "sum",
            "Unique impressions (organic)": "sum",
        })
        .reset_index()
    )
    monthly["month"] = monthly["Date"].dt.strftime("%Y-%m")
    monthly["reach_ratio"] = (
        monthly["Unique impressions (organic)"] / monthly["Impressions (total)"]
    ).round(3)
    monthly["imp_change_pct"] = monthly["Impressions (total)"].pct_change().round(3) * 100

    return {
        "total_impressions": total_imp,
        "total_unique_impressions": unique_imp,
        "avg_daily_impressions": round(df["Impressions (total)"].mean(), 1),
        "max_daily_impressions": int(df["Impressions (total)"].max()),
        "overall_reach_ratio": round(unique_imp / total_imp, 3) if total_imp > 0 else 0,
        "has_sponsored": bool(df["Impressions (sponsored)"].sum() > 0),
        "monthly": monthly[["month", "Impressions (total)", "Unique impressions (organic)", "reach_ratio", "imp_change_pct"]].to_dict(orient="records"),
    }


# ---------------------------------------------------------------------------
# 5. FOLLOWER-ENGAGEMENT CORRELATION
# ---------------------------------------------------------------------------

def calculate_follower_engagement_correlation(df_content: pd.DataFrame, df_followers: pd.DataFrame) -> dict:
    """
    Analyze the relationship between content performance and follower growth
    on overlapping dates.

    Returns:
        dict with correlation stats and monthly comparison
    """
    # Merge on overlapping dates
    df_c = df_content[["Date", "Impressions (total)", "Total Engagement", "Engagement rate (total)"]].copy()
    df_f = df_followers[["Date", "Total followers", "Cumulative Followers"]].copy()

    merged = pd.merge(df_c, df_f, on="Date", how="inner")

    if len(merged) == 0:
        return {"overlap_days": 0, "note": "No overlapping dates between content and follower data."}

    # Daily correlations
    corr_imp = round(merged["Impressions (total)"].corr(merged["Total followers"]), 3)
    corr_eng = round(merged["Total Engagement"].corr(merged["Total followers"]), 3)

    # Monthly comparison
    monthly = merged.set_index("Date").resample("ME").agg({
        "Impressions (total)": "sum",
        "Total Engagement": "sum",
        "Total followers": "sum",
    }).reset_index()
    monthly["month"] = monthly["Date"].dt.strftime("%Y-%m")
    monthly_corr = round(monthly["Impressions (total)"].corr(monthly["Total followers"]), 3)

    # Follower efficiency: new followers per 1000 impressions
    total_imp = merged["Impressions (total)"].sum()
    total_fol = merged["Total followers"].sum()
    efficiency = round(total_fol / (total_imp / 1000), 2) if total_imp > 0 else 0

    return {
        "overlap_days": len(merged),
        "overlap_range": f"{merged['Date'].min().strftime('%Y-%m-%d')} to {merged['Date'].max().strftime('%Y-%m-%d')}",
        "daily_correlation_impressions_followers": corr_imp,
        "daily_correlation_engagement_followers": corr_eng,
        "monthly_correlation_impressions_followers": monthly_corr,
        "followers_per_1000_impressions": efficiency,
        "monthly_comparison": monthly[["month", "Impressions (total)", "Total Engagement", "Total followers"]].to_dict(orient="records"),
    }


# ---------------------------------------------------------------------------
# TOP PERFORMING DAYS
# ---------------------------------------------------------------------------

def get_top_days(df: pd.DataFrame, n: int = 10) -> list:
    """Return the top N days by impressions."""
    top = df.nlargest(n, "Impressions (total)")
    return top[["Date", "Impressions (total)", "Clicks (total)", "Reactions (total)",
                 "Comments (total)", "Engagement rate (total)", "Total Engagement"]].to_dict(orient="records")


# ---------------------------------------------------------------------------
# FULL ANALYSIS REPORT
# ---------------------------------------------------------------------------

def run_full_analysis(content_csv: str, followers_csv: str = None) -> dict:
    """
    Run the complete analysis pipeline and return all metrics.

    Args:
        content_csv: Path to the clean content CSV file.
        followers_csv: Path to the clean followers CSV file (optional).

    Returns:
        dict with all computed metrics.
    """
    df = load_data(content_csv)

    report = {
        "data_summary": {
            "content_file": os.path.basename(content_csv),
            "content_date_range": f"{df['Date'].min().strftime('%Y-%m-%d')} to {df['Date'].max().strftime('%Y-%m-%d')}",
            "content_days": len(df),
        },
        "engagement_rate": calculate_engagement_rate(df),
        "post_frequency": calculate_post_frequency(df),
        "reach": calculate_reach(df),
        "top_performing_days": get_top_days(df),
    }

    # Add follower data if available
    if followers_csv and os.path.exists(followers_csv):
        df_f = load_followers(followers_csv)
        report["data_summary"]["followers_file"] = os.path.basename(followers_csv)
        report["data_summary"]["followers_date_range"] = f"{df_f['Date'].min().strftime('%Y-%m-%d')} to {df_f['Date'].max().strftime('%Y-%m-%d')}"
        report["data_summary"]["followers_days"] = len(df_f)
        report["followers"] = calculate_followers(df_f)
        report["follower_engagement_correlation"] = calculate_follower_engagement_correlation(df, df_f)
    else:
        report["followers"] = {"note": "No followers data provided. Use --followers flag to include."}

    return report


def save_report(report: dict, output_path: str) -> None:
    """Save the analysis report as JSON."""
    def default_serializer(obj):
        if isinstance(obj, (pd.Timestamp, np.integer)):
            return str(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

    with open(output_path, "w") as f:
        json.dump(report, f, indent=2, default=default_serializer)
    print(f"[OK] Report saved to: {output_path}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python analysis.py <content_csv> [output_json] [--followers <followers_csv>]")
        print("\nExamples:")
        print("  python analysis.py data/women_in_ai_usa_clean.csv")
        print("  python analysis.py data/women_in_ai_usa_clean.csv data/report.json --followers data/women_in_ai_usa_followers.csv")
        sys.exit(1)

    content_file = sys.argv[1]

    # Parse optional args
    output_file = "data/analysis_report.json"
    followers_file = None

    args = sys.argv[2:]
    i = 0
    while i < len(args):
        if args[i] == "--followers" and i + 1 < len(args):
            followers_file = args[i + 1]
            i += 2
        elif not args[i].startswith("--"):
            output_file = args[i]
            i += 1
        else:
            i += 1

    report = run_full_analysis(content_file, followers_file)
    save_report(report, output_file)

    # Print summary
    print(f"\n{'='*60}")
    print(f"  ANALYSIS COMPLETE")
    print(f"{'='*60}")
    print(f"  Content Date Range: {report['data_summary']['content_date_range']}")
    print(f"  Content Days:       {report['data_summary']['content_days']}")
    print(f"  Total Impressions:  {report['reach']['total_impressions']:,}")
    print(f"  Unique Reach:       {report['reach']['total_unique_impressions']:,}")
    print(f"  Total Engagement:   {report['engagement_rate']['total_engagement']:,}")
    print(f"  Avg Eng. Rate:      {report['engagement_rate']['daily_avg_rate']*100:.2f}%")
    print(f"  Active Days:        {report['post_frequency']['active_days']}/{report['post_frequency']['total_days']}")
    print(f"  Best Posting Days:  {', '.join(report['post_frequency']['best_posting_days'])}")

    if followers_file and "followers" in report and "total_gained" in report["followers"]:
        f = report["followers"]
        print(f"  ────────────────────────────────────")
        print(f"  Followers Gained:   {f['total_gained']:,} (100% organic)")
        print(f"  Avg Daily New:      {f['avg_daily_new']}")
        print(f"  Best Month:         {f['best_month']['month']} (+{f['best_month']['gained']})")
        print(f"  Worst Month:        {f['worst_month']['month']} (+{f['worst_month']['gained']})")
        print(f"  Growth Trend:       {f['growth_trend_pct']:+.1f}%")
        if "follower_engagement_correlation" in report:
            c = report["follower_engagement_correlation"]
            print(f"  Followers/1K Imp:   {c['followers_per_1000_impressions']}")
            print(f"  Monthly Corr:       {c['monthly_correlation_impressions_followers']}")

    print(f"{'='*60}\n")