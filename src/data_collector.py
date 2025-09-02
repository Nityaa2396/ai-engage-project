import tweepy
import pandas as pd
from datetime import datetime
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import os
from dotenv import load_dotenv

load_dotenv()
bearer_token = os.getenv("TWITTER_BEARER_TOKEN")
client = tweepy.Client(bearer_token=bearer_token)

nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)
analyzer = SentimentIntensityAnalyzer()

def clean_text(text):
    tokens = word_tokenize(text.lower())
    stop_words = set(stopwords.words('english'))
    cleaned = ' '.join([word for word in tokens if word.isalnum() and word not in stop_words])
    return cleaned

def get_sentiment(text):
    return analyzer.polarity_scores(text)['compound']

def collect_women_in_ai_data():
    try:
        query = '"Women in AI" OR #WomenInAI -is:retweet lang:en'
        tweets = client.search_recent_tweets(
            query=query,
            tweet_fields=['created_at', 'public_metrics'],
            max_results=10
        )

        if not tweets.data:
            print("No tweets found!")
            return

        data = []
        for tweet in tweets.data:
            post = {
                'text': tweet.text,
                'likes': tweet.public_metrics['like_count'],
                'reposts': tweet.public_metrics['retweet_count'],
                'replies': tweet.public_metrics['reply_count'],
                'timestamp': tweet.created_at,
                'has_media': 'media' in tweet.text.lower() or 'https://t.co' in tweet.text
            }
            data.append(post)

        df = pd.DataFrame(data)
        df['cleaned_text'] = df['text'].apply(clean_text)
        df['has_hashtag'] = df['text'].str.contains('#')
        df['engagement'] = df['likes'] + df['reposts'] + 0.5 * df['replies']
        df['sentiment_score'] = df['text'].apply(get_sentiment)
        df['word_count'] = df['text'].apply(lambda x: len(x.split()))
        df.to_csv('data/cleaned_women_in_ai_posts.csv', index=False)
        print(f"Collected {len(df)} posts for Women in AI analysis!")

    except Exception as e:
        print(f"Error collecting data: {e}")

if __name__ == "__main__":
    collect_women_in_ai_data()