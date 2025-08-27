import tweepy
import pandas as pd
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import os

# Function to fetch Women in AI posts from X (or load LinkedIn CSV)
def collect_women_in_ai_posts(bearer_token=None, use_csv=False):
    """Collects posts for Women in AI analysis, either from X or a CSV for LinkedIn data."""
    women_in_ai_posts_df = pd.DataFrame()
    
    if use_csv:
        # For LinkedIn, assume user exports analytics to CSV
        try:
            women_in_ai_posts_df = pd.read_csv('data/sample_women_in_ai_posts.csv')
            print("Loaded LinkedIn data from CSV!")
        except FileNotFoundError:
            print("CSV not found, using sample data instead.")
            women_in_ai_posts_df = pd.read_csv('data/sample_women_in_ai_posts.csv')
    else:
        # Fetch from X using Tweepy
        try:
            client = tweepy.Client(bearer_token=bearer_token)
            tweets = client.get_users_tweets(id='871111526282911746', max_results=100)  # Women in AI's X ID
            data = [
                {
                    'text': tweet.text,
                    'likes': tweet.public_metrics['like_count'],
                    'reposts': tweet.public_metrics['retweet_count'],
                    'replies': tweet.public_metrics['reply_count'],
                    'timestamp': tweet.created_at,
                    'has_media': 'media' in tweet.attachments if tweet.attachments else False
                } for tweet in tweets.data
            ]
            women_in_ai_posts_df = pd.DataFrame(data)
        except Exception as e:
            print(f"Error fetching X data: {e}. Using sample CSV.")
            women_in_ai_posts_df = pd.read_csv('data/sample_women_in_ai_posts.csv')
    
    # Clean text for analysis
    stop_words = set(stopwords.words('english'))
    women_in_ai_posts_df['clean_text'] = women_in_ai_posts_df['text'].apply(
        lambda x: ' '.join([word for word in word_tokenize(x.lower()) if word.isalpha() and word not in stop_words])
    )
    women_in_ai_posts_df['word_count'] = women_in_ai_posts_df['text'].apply(lambda x: len(x.split()))
    women_in_ai_posts_df['has_hashtag'] = women_in_ai_posts_df['text'].apply(lambda x: '#' in x)
    
    # Save cleaned data
    os.makedirs('data', exist_ok=True)
    women_in_ai_posts_df.to_csv('data/cleaned_women_in_ai_posts.csv', index=False)
    return women_in_ai_posts_df

if __name__ == "__main__":
    # Replace with your X API bearer token or set use_csv=True for LinkedIn
    posts_df = collect_women_in_ai_posts(bearer_token='YOUR_BEARER_TOKEN', use_csv=True)
    print(f"Collected {len(posts_df)} posts for Women in AI analysis!")