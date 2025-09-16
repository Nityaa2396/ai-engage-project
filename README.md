## Women in AI: Data Exploration & Manual Annotation

### Data Collection

- **Twitter/X**: `data_collector.py` uses Twitter/X API v2 to fetch posts with query `"Women in AI" OR #WomenInAI`, saving to `cleaned_women_in_ai_posts.csv`.
- **LinkedIn**: `convert_xls_to_csv.py` converts `linkedin_analytics.xls` to `linkedin_women_in_ai_posts.csv`. `linkedin_data_collector.py` processes it, adding features.

### Manual Annotation

- **Post Content**: Manually added to `linkedin_women_in_ai_posts.csv` by copying text from Women in AI LinkedIn Page posts matching dates in `linkedin_analytics.xls`.
- **Theme Labeling**: Added `theme` column (e.g., AI ethics, Event, Diversity) based on post content analysis.
- **Guidelines**:
  - **AI ethics**: Posts discussing AI fairness, bias, or ethical issues.
  - **Event**: Posts about conferences, webinars, or summits.
  - **Diversity**: Posts highlighting individuals or diversity in AI.
  - Ensure `text` is non-empty and quoted to handle commas.
  - Verify `has_media` (True for image/video, False otherwise).

### Processing

- Both scripts compute:
  - `cleaned_text`: Lowercased, stopwords removed.
  - `has_hashtag`: True if post contains `#`.
  - `engagement`: likes + reposts + 0.5 \* replies.
  - `sentiment_score`: VADER sentiment analysis.
  - `word_count`: Number of words in `text`.

### Visualization

- `analysis.ipynb` includes word cloud, engagement trends, and hashtag analysis.
- Added: Theme distribution, missing data heatmap.
