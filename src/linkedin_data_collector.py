import pandas as pd
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)
analyzer = SentimentIntensityAnalyzer()

def clean_text(text):
    tokens = word_tokenize(str(text).lower())
    stop_words = set(stopwords.words('english'))
    cleaned = ' '.join([word for word in tokens if word.isalnum() and word not in stop_words])
    return cleaned

def get_sentiment(text):
    return analyzer.polarity_scores(str(text))['compound']

def collect_linkedin_women_in_ai_data():
    try:
        df = pd.read_csv('data/linkedin_women_in_ai_posts.csv')
        df['cleaned_text'] = df['text'].apply(clean_text)
        df['has_hashtag'] = df['text'].str.contains('#', na=False)
        df['engagement'] = df['likes'] + df['reposts'] + 0.5 * df['replies']
        df['sentiment_score'] = df['text'].apply(get_sentiment)
        df['word_count'] = df['text'].apply(lambda x: len(str(x).split()))
        columns = ['text', 'likes', 'reposts', 'replies', 'timestamp', 'has_media', 'theme', 'cleaned_text', 'has_hashtag', 'engagement', 'sentiment_score', 'word_count']
        df = df[[col for col in columns if col in df.columns]]
        df.to_csv('data/cleaned_women_in_ai_posts.csv', index=False)
        print(f"Loaded LinkedIn data from CSV!\nCollected {len(df)} posts for Women in AI analysis!")
    except Exception as e:
        print(f"Error collecting data: {e}")

if __name__ == "__main__":
    collect_linkedin_women_in_ai_data()