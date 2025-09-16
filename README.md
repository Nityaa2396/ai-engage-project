# Women in AI: Data Exploration & Manual Annotation

This project focuses on collecting, annotating, and analyzing social media posts related to "Women in AI," with an emphasis on both automation and thoughtful manual review.

---

## 1. Data Collection

- **Twitter/X**  
  - `data_collector.py`: Utilizes Twitter/X API v2 to gather posts matching the queries `"Women in AI"` or `#WomenInAI`.
  - Output: Cleaned results are saved to `cleaned_women_in_ai_posts.csv`.

- **LinkedIn**  
  - `convert_xls_to_csv.py`: Converts LinkedIn analytics data from `linkedin_analytics.xls` to CSV format (`linkedin_women_in_ai_posts.csv`).
  - `linkedin_data_collector.py`: Processes LinkedIn posts and enriches them with additional features.

---

## 2. Manual Annotation

- **Post Content**  
  - Text is manually extracted from Women in AI LinkedIn Page posts, aligning post dates with those in `linkedin_analytics.xls`.

- **Theme Labeling**  
  - Each post is assigned a `theme` (e.g., *AI ethics*, *Event*, *Diversity*) based on its content.

#### Annotation Guidelines

- **AI ethics**: Posts discussing fairness, bias, or ethical dimensions of AI.
- **Event**: Announcements about conferences, webinars, or summits.
- **Diversity**: Highlights about individuals or diversity initiatives within AI.

- Ensure post text is non-empty and enclosed in quotes (to handle commas).
- Validate the `has_media` field: `True` for image/video, `False` otherwise.

---

## 3. Data Processing

Both Twitter/X and LinkedIn scripts compute the following features:

- **cleaned_text**: Lowercased, with stopwords removed.
- **has_hashtag**: Boolean indicating presence of hashtags.
- **engagement**: Computed as `likes + reposts + 0.5 * replies`.
- **sentiment_score**: Based on VADER sentiment analysis.
- **word_count**: Number of words in the post.

---

## 4. Visualization & Analysis

Explore insights in `analysis.ipynb`, including:

- Word cloud visualizations
- Engagement trend charts
- Hashtag usage analysis
- Theme distribution across posts
- Missing data heatmap

---

## Project Highlights

- Multi-platform data pipeline (Twitter/X & LinkedIn)
- Balanced approach: automation + human annotation
- Rich feature engineering for downstream analysis
- Visual storytelling of Women in AI social media impact

---

*Feel free to contribute, raise issues, or reach out for collaboration!*
