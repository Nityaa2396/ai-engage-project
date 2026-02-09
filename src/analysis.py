"""
analysis.py — Core metric calculations for LinkedIn social media analytics.

Metrics tracked:
    1. Followers (proxy via unique impressions — LinkedIn exports don't include follower count)
    2. Engagement Rate = (Clicks + Reactions + Comments + Reposts) / Impressions
    3. Post Frequency = Days with meaningful engagement activity
    4. Reach = Total and unique impressions over time

All functions accept a pandas DataFrame with the standard LinkedIn export schema.
"""

import pandas as pd
import numpy as np
import json
import os


def load_data(csv_path: str) -> pd.DataFrame:
    """Load and prepare the clean CSV data."""
    df = pd.read_csv(csv_path)
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values("Date").reset_index(drop=True)

    # Ensure Total Engagement exists
    if "Total Engagement" not in df.columns:
        df["Total Engagement"] = (
            df["Clicks (total)"]
            + df["Reactions (total)"]
            + df["Comments (total)"]
            + df["Reposts (total)"]
        )
    return df


# ---------------------------------------------------------------------------
# 1. FOLLOWERS (PROXY)
# ---------------------------------------------------------------------------

def calculate_followers_proxy(df: pd.DataFrame) -> dict:
    """
    LinkedIn page analytics exports don't include follower counts.
    We use cumulative unique impressions as a reach/audience proxy.

    Returns:
        dict with total_unique_impressions, avg_daily, monthly_unique, growth_trend
    """
    monthly = (
        df.set_index("Date")
        .resample("ME")["Unique impressions (organic)"]
        .agg(["sum", "mean", "max"])
        .rename(columns={"sum": "total", "mean": "daily_avg", "max": "peak_day"})
    )

    # Growth trend: compare last 3 months vs first 3 months
    months = monthly.index.tolist()
    if len(months) >= 6:
        first_3 = monthly.iloc[:3]["total"].mean()
        last_3 = monthly.iloc[-3:]["total"].mean()
        growth = ((last_3 - first_3) / first_3) * 100 if first_3 > 0 else 0
    else:
        growth = 0

    return {
        "total_unique_impressions": int(df["Unique impressions (organic)"].sum()),
        "avg_daily_unique": round(df["Unique impressions (organic)"].mean(), 1),
        "max_daily_unique": int(df["Unique impressions (organic)"].max()),
        "monthly_breakdown": monthly.reset_index().to_dict(orient="records"),
        "audience_growth_pct": round(growth, 1),
    }


# ---------------------------------------------------------------------------
# 2. ENGAGEMENT RATE
# ---------------------------------------------------------------------------

def calculate_engagement_rate(df: pd.DataFrame) -> dict:
    """
    Engagement Rate = (Clicks + Reactions + Comments + Reposts) / Impressions.

    LinkedIn provides this natively, but we also compute it independently for
    verification and breakdown analysis.

    Returns:
        dict with overall, daily_avg, monthly, weekly_trend, by_component
    """
    total_eng = df["Total Engagement"].sum()
    total_imp = df["Impressions (total)"].sum()
    overall_rate = total_eng / total_imp if total_imp > 0 else 0

    # Daily average (matches LinkedIn's daily metric)
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
    LinkedIn exports daily aggregates, not per-post data.
    Post frequency is approximated by:
    - Days with any engagement (proxy for days a post was active/visible)
    - Spikes in impressions (likely new post days)

    Returns:
        dict with active_days, total_days, frequency metrics, spike detection
    """
    total_days = len(df)
    active_days = int((df["Total Engagement"] > 0).sum())

    # Detect impression spikes (days > 1.5x the rolling 7-day average)
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

    # Monthly
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

    # Month-over-month changes
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

def run_full_analysis(csv_path: str) -> dict:
    """
    Run the complete analysis pipeline and return all metrics.

    Args:
        csv_path: Path to the clean CSV file.

    Returns:
        dict with all computed metrics.
    """
    df = load_data(csv_path)

    report = {
        "data_summary": {
            "source_file": os.path.basename(csv_path),
            "date_range": f"{df['Date'].min().strftime('%Y-%m-%d')} to {df['Date'].max().strftime('%Y-%m-%d')}",
            "total_days": len(df),
            "columns": len(df.columns),
        },
        "followers_proxy": calculate_followers_proxy(df),
        "engagement_rate": calculate_engagement_rate(df),
        "post_frequency": calculate_post_frequency(df),
        "reach": calculate_reach(df),
        "top_performing_days": get_top_days(df),
    }

    return report


def save_report(report: dict, output_path: str) -> None:
    """Save the analysis report as JSON."""
    # Convert any non-serializable types
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
        print("Usage: python analysis.py <path_to_csv> [output_json_path]")
        sys.exit(1)

    csv_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "data/analysis_report.json"

    report = run_full_analysis(csv_file)
    save_report(report, output_file)

    # Print summary to console
    print(f"\n{'='*60}")
    print(f"  ANALYSIS COMPLETE")
    print(f"{'='*60}")
    print(f"  Date Range:        {report['data_summary']['date_range']}")
    print(f"  Total Days:        {report['data_summary']['total_days']}")
    print(f"  Total Impressions: {report['reach']['total_impressions']:,}")
    print(f"  Unique Reach:      {report['reach']['total_unique_impressions']:,}")
    print(f"  Total Engagement:  {report['engagement_rate']['total_engagement']:,}")
    print(f"  Avg Eng. Rate:     {report['engagement_rate']['daily_avg_rate']*100:.2f}%")
    print(f"  Active Days:       {report['post_frequency']['active_days']}/{report['post_frequency']['total_days']}")
    print(f"  Best Posting Days: {', '.join(report['post_frequency']['best_posting_days'])}")
    print(f"  Audience Growth:   {report['followers_proxy']['audience_growth_pct']:+.1f}%")
    print(f"{'='*60}\n")