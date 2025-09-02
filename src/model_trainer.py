import pandas as pd
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

def train_engagement_predictor():
    """Trains a model to predict engagement for Women in AI social posts."""
    # Load cleaned data
    women_in_ai_posts_df = pd.read_csv('data/cleaned_women_in_ai_posts.csv')
    
    # Add sentiment feature
    analyzer = SentimentIntensityAnalyzer()
    women_in_ai_posts_df['sentiment_score'] = women_in_ai_posts_df['text'].apply(
        lambda x: analyzer.polarity_scores(x)['compound']
    )
    
    # Create engagement target (likes + reposts + 0.5 * replies)
    women_in_ai_posts_df['engagement'] = (
        women_in_ai_posts_df['likes'] + 
        women_in_ai_posts_df['reposts'] + 
        0.5 * women_in_ai_posts_df['replies']
    )
    
    # Features: TF-IDF + numerical
    tfidf_vectorizer = TfidfVectorizer(max_features=500)
    text_features = tfidf_vectorizer.fit_transform(women_in_ai_posts_df['cleaned_text'])
    feature_df = pd.concat([
        pd.DataFrame(text_features.toarray()),
        women_in_ai_posts_df[['sentiment_score', 'word_count', 'has_hashtag', 'has_media']].reset_index(drop=True)
    ], axis=1)
    
    # Convert column names to strings (for sklearn compatibility)
    feature_df.columns = feature_df.columns.astype(str)
    
    X = feature_df
    y = women_in_ai_posts_df['engagement']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train model
    engagement_model = RandomForestRegressor(n_estimators=100, random_state=42)
    engagement_model.fit(X_train, y_train)
    
    # Evaluate
    predictions = engagement_model.predict(X_test)
    mse = mean_squared_error(y_test, predictions)
    print(f"Model MSE: {mse:.2f}")
    
    # Save model and vectorizer
    with open('models/engagement_model.pkl', 'wb') as f:
        pickle.dump(engagement_model, f)
    with open('models/tfidf_vectorizer.pkl', 'wb') as f:
        pickle.dump(tfidf_vectorizer, f)
    
    return engagement_model, tfidf_vectorizer

if __name__ == "__main__":
    import os
    os.makedirs('models', exist_ok=True)
    model, vectorizer = train_engagement_predictor()
    print("Engagement predictor trained and saved!")
