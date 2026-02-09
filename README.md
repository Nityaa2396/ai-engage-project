# Women in AI USA — LinkedIn Social Media Analytics

A Python-based analytics pipeline for tracking and visualizing LinkedIn page performance metrics for the **Women in AI USA** community.

## Metrics Tracked

| Metric                | Description                                              | Source                                                |
| --------------------- | -------------------------------------------------------- | ----------------------------------------------------- |
| **Followers (Proxy)** | Cumulative unique impressions as audience reach proxy    | `Unique impressions (organic)`                        |
| **Engagement Rate**   | (Clicks + Reactions + Comments + Reposts) / Impressions  | `Engagement rate (total)`                             |
| **Post Frequency**    | Days with active engagement + impression spike detection | Computed from daily data                              |
| **Reach**             | Total and unique impressions over time                   | `Impressions (total)`, `Unique impressions (organic)` |

## Project Structure

```
ai-engage-project/
├── data/
│   ├── women_in_ai_usa_clean.csv      # Cleaned daily data (365 days)
│   └── analysis_report.json           # Full analysis output
├── figures/
│   ├── impressions_trend.png           # Daily impressions + 7d rolling avg
│   ├── engagement_rate_trend.png       # Engagement rate over time
│   ├── monthly_summary.png             # Monthly bars + engagement line
│   ├── day_of_week.png                 # Day-of-week performance
│   ├── engagement_composition.png      # Clicks/reactions/comments/reposts
│   ├── reach_analysis.png              # Total vs unique impressions
│   └── top_days.png                    # Top 10 performing days
├── src/
│   ├── __init__.py
│   ├── analysis.py                     # Core metric calculations
│   ├── data_validation.py              # Data quality checks
│   └── visualizations.py               # Chart generation (matplotlib)
├── notebooks/                          # Jupyter notebooks (optional)
├── models/                             # ML models (future)
├── convert_xls_to_csv.py              # XLS → CSV converter
├── requirements.txt
└── README.md
```

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Convert XLS to Clean CSV

```bash
python convert_xls_to_csv.py <path_to_xls_file>
```

This will:

- Read the `.xls` file (with LibreOffice fallback for encoding issues)
- Standardize dates to `YYYY-MM-DD` format
- Add a computed `Total Engagement` column
- Save to `data/women_in_ai_usa_clean.csv`

### 3. Validate Data

```bash
python src/data_validation.py data/women_in_ai_usa_clean.csv
```

Checks for: missing columns, null values, date gaps, duplicates, negative values, type consistency.

### 4. Run Analysis

```bash
python src/analysis.py data/women_in_ai_usa_clean.csv data/analysis_report.json
```

Computes all four core metrics and saves a detailed JSON report.

### 5. Generate Charts

```bash
python src/visualizations.py data/women_in_ai_usa_clean.csv figures/
```

Produces 7 publication-ready charts in the `figures/` directory.

### Run Everything at Once

```bash
python convert_xls_to_csv.py your_file.xls
python src/data_validation.py data/women_in_ai_usa_clean.csv
python src/analysis.py data/women_in_ai_usa_clean.csv data/analysis_report.json
python src/visualizations.py data/women_in_ai_usa_clean.csv figures/
```

## Key Findings (Jan 28, 2025 – Jan 27, 2026)

- **170,398** total impressions across 365 days
- **82,054** unique viewers (48.2% reach ratio)
- **8.25%** average daily engagement rate
- **16,171** total engagements (69.8% clicks, 27.0% reactions, 2.4% comments, 0.8% reposts)
- **360/365** days showed engagement activity (98.6% activity rate)
- Peak days: June 9, 2025 (3,755 impressions) and November 13, 2025 (3,387 impressions)
- Best posting days: **Wednesday, Tuesday, Friday**
- All content is 100% organic — no sponsored posts

## Data Validation Notes

- **Zero null values** across all 365 rows × 20 columns
- **3 minor negative values** in reactions/comments/reposts (LinkedIn data corrections from user undo actions)
- **All sponsored columns are zero** — exclusively organic content
- Date coverage is continuous with no gaps

## Metric Calculation Details

### Engagement Rate

LinkedIn's native formula: `(Clicks + Reactions + Comments + Reposts) / Impressions`

The pipeline computes this independently for verification and also provides the 7-day rolling average for trend analysis.

### Post Frequency (Proxy)

Since LinkedIn exports daily aggregates rather than per-post data, post frequency is estimated via:

1. **Active days**: Days where total engagement > 0
2. **Spike detection**: Days where impressions exceed 1.5× the 7-day rolling average (indicative of new post publication)

### Reach Ratio

`Unique Impressions / Total Impressions` — measures how much of the audience is new vs. repeat viewers. A ratio closer to 1.0 means more unique reach; lower values indicate repeat views of content.

## Assumptions

1. LinkedIn's 2-day data delay means the most recent 1-2 days may be incomplete.
2. Negative values in count columns are treated as LinkedIn data corrections (post edits, undo actions).
3. "Followers" metric uses unique impressions as a proxy since LinkedIn page analytics exports do not include follower counts directly.
4. Post frequency is estimated, not exact, due to daily-aggregate export format.

## License

Internal project — Women in AI USA.
