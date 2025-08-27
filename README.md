# AI-Engage: Social Media Optimizer for Women in AI

This project helps Women in AI, a non-profit empowering women in AI, optimize LinkedIn and X posts for better engagement. As the marketing team lead, I built this to analyze past posts, predict engagement, and suggest improvements.

## Features

- **Data Collection**: Fetches posts from X or uses LinkedIn CSV exports.
- **Analysis**: Visualizes engagement trends and key topics (e.g., AI ethics).
- **Prediction**: Uses Random Forest to predict likes/reposts for new posts.
- **Dashboard**: Streamlit app to input draft posts and get tailored tips.

## Setup

1. Clone the repo: `git clone <your-repo-url>`
2. Install dependencies: `pip install -r requirements.txt`
3. For X data, add your bearer token to `data_collector.py`.
4. Run analysis: `jupyter notebook notebooks/analysis.ipynb`
5. Launch app: `streamlit run src/app.py`

## Data

- Sample data in `data/sample_women_in_ai_posts.csv` (replace with your LinkedIn export).
- Columns: text, likes, reposts, replies, timestamp, etc.

## Future Ideas

- Add topic modeling for post clustering.
- Integrate fairness checks for inclusive language.

Built by [Your Name] for Women in AI.

```

```
