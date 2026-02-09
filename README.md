# Women in AI USA — LinkedIn Social Media Analytics

A Python-based analytics pipeline for tracking and visualizing LinkedIn page performance metrics for the **Women in AI USA** community.

## Metrics Tracked

| #   | Metric              | Description                                                  | Source                                                |
| --- | ------------------- | ------------------------------------------------------------ | ----------------------------------------------------- |
| 1   | **Followers**       | Real follower growth — daily new, cumulative, monthly trends | `women_in_ai_usa_followers.csv`                       |
| 2   | **Engagement Rate** | (Clicks + Reactions + Comments + Reposts) / Impressions      | `Engagement rate (total)`                             |
| 3   | **Post Frequency**  | Days with active engagement + impression spike detection     | Computed from daily data                              |
| 4   | **Reach**           | Total and unique impressions over time                       | `Impressions (total)`, `Unique impressions (organic)` |

## Project Structure

```
ai-engage-project/
├── data/
│   ├── women_in_ai_usa_clean.csv       # Cleaned content data (365 days)
│   ├── women_in_ai_usa_followers.csv   # Cleaned follower data (365 days)
│   └── analysis_report.json            # Full analysis output (JSON)
├── figures/
│   ├── impressions_trend.png           # Daily impressions + 7d rolling avg
│   ├── engagement_rate_trend.png       # Engagement rate over time
│   ├── monthly_summary.png             # Monthly bars + engagement line
│   ├── day_of_week.png                 # Day-of-week performance
│   ├── engagement_composition.png      # Clicks/reactions/comments/reposts
│   ├── reach_analysis.png              # Total vs unique impressions
│   ├── top_days.png                    # Top 10 performing days
│   ├── follower_growth.png             # Daily + cumulative follower growth
│   ├── follower_monthly.png            # Monthly new followers
│   └── follower_vs_engagement.png      # Followers vs content performance
├── src/
│   ├── __init__.py
│   ├── analysis.py                     # Core metric calculations
│   ├── data_validation.py              # Data quality checks
│   └── visualizations.py               # Chart generation (matplotlib)
├── notebooks/
├── models/
├── convert_xls_to_csv.py              # XLS → CSV converter (content + followers)
├── requirements.txt
└── README.md
```

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Convert XLS Exports to Clean CSVs

```bash
# Content analytics export
python convert_xls_to_csv.py data/content_export.xls data/women_in_ai_usa_clean.csv content

# Follower metrics export
python convert_xls_to_csv.py data/followers_export.xls data/women_in_ai_usa_followers.csv followers

# Or auto-detect type
python convert_xls_to_csv.py data/any_export.xls
```

### 3. Validate Data

```bash
python src/data_validation.py data/women_in_ai_usa_clean.csv data/women_in_ai_usa_followers.csv
```

### 4. Run Analysis

```bash
python src/analysis.py data/women_in_ai_usa_clean.csv data/analysis_report.json --followers data/women_in_ai_usa_followers.csv
```

### 5. Generate Charts

```bash
python src/visualizations.py data/women_in_ai_usa_clean.csv figures/ --followers data/women_in_ai_usa_followers.csv
```

### Run Everything at Once

```bash
python convert_xls_to_csv.py data/content_export.xls data/women_in_ai_usa_clean.csv content
python convert_xls_to_csv.py data/followers_export.xls data/women_in_ai_usa_followers.csv followers
python src/data_validation.py data/women_in_ai_usa_clean.csv data/women_in_ai_usa_followers.csv
python src/analysis.py data/women_in_ai_usa_clean.csv data/analysis_report.json --followers data/women_in_ai_usa_followers.csv
python src/visualizations.py data/women_in_ai_usa_clean.csv figures/ --followers data/women_in_ai_usa_followers.csv
```

## Key Findings

### Content Performance (Jan 28, 2025 – Jan 27, 2026)

- **170,398** total impressions across 365 days
- **82,054** unique viewers (48.2% reach ratio)
- **8.25%** average daily engagement rate (2–4x nonprofit benchmark)
- **16,171** total engagements (69.8% clicks, 27.0% reactions, 2.4% comments, 0.8% reposts)
- **360/365** days showed engagement activity (98.6% activity rate)
- Peak days: June 9, 2025 (3,755 impressions) and November 13, 2025 (3,387 impressions)
- Best posting days: **Wednesday, Tuesday, Friday**

### Follower Growth (Feb 8, 2025 – Feb 7, 2026)

- **2,200** new followers gained (100% organic, zero sponsored)
- **6.03** average new followers per day
- Best month: **April 2025** (+324 followers)
- Worst month: **December 2025** (+86 followers)
- **0.855 monthly correlation** between impressions and follower growth
- **12.7 followers gained per 1,000 impressions**
- 14 days with zero new followers, 3 days with net unfollows

### Cross-Metric Insights

- Strong monthly correlation (0.855) between content impressions and follower growth confirms that content drives audience growth
- April and June spikes in both impressions and followers suggest successful campaigns
- December showed high engagement rate (11.95%) but lowest follower growth — engaged but saturated audience
- All content is 100% organic — no sponsored posts or paid follower acquisition

## Data Notes

- **Date ranges differ**: Content data starts Jan 28, 2025; follower data starts Feb 8, 2025. Analysis uses overlapping dates (Feb 8, 2025 – Jan 27, 2026) for correlation metrics.
- **Zero null values** in both datasets.
- **3 negative values** in content data (LinkedIn corrections from undo actions).
- **3 negative follower days** (net unfollows).
- **All sponsored columns are zero** across both datasets.

## Metric Formulas

- **Engagement Rate**: `(Clicks + Reactions + Comments + Reposts) / Impressions`
- **Post Frequency (Proxy)**: Days where engagement > 0, plus spike detection (impressions > 1.5× 7-day rolling avg)
- **Reach Ratio**: `Unique Impressions / Total Impressions`
- **Follower Efficiency**: `New Followers / (Impressions / 1000)`
- **Growth Trend**: Compares average of last 3 months vs first 3 months

## License

Internal project — Women in AI USA.
