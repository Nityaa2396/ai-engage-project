import streamlit as st
import pandas as pd
import pickle
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Load models
@st.cache_resource
def load_models():
    with open('models/engagement_model.pkl', 'rb') as f:
        model = pickle.load(f)
    with open('models/tfidf_vectorizer.pkl', 'rb') as f:
        vectorizer = pickle.load(f)
    return model, vectorizer

# Function to suggest improvements
def suggest_diversity_post_content(post_text, predicted_engagement):
    """Custom suggestions for Women in AI posts."""
    suggestions = []
    if predicted_engagement < 5:
        suggestions.append("Engagement seems low. Try adding a question (e.g., 'What's your take on AI ethics?') to spark replies.")
    if '#' not in post_text:
        suggestions.append("Add hashtags like #WomenInAI or #AIEthics to reach more people.")
    if len(post_text.split()) > 100:
        suggestions.append("Post is long. Shorten to 50-80 words for better LinkedIn engagement.")
    if 'event' in post_text.lower():
        suggestions.append("Events are great! Include a registration link or image to boost clicks.")
    return suggestions

# Streamlit app
st.title("AI-Engage: Women in AI Post Optimizer")
st.write("Enter a draft post to predict engagement and get tips for better LinkedIn performance!")

# Load model and vectorizer
engagement_model, tfidf_vectorizer = load_models()

# Text input
post_text = st.text_area("Draft your Women in AI post:", height=150)

if st.button("Analyze Post"):
    if post_text:
        # Preprocess input
        stop_words = set(stopwords.words('english'))
        clean_text = ' '.join([word for word in word_tokenize(post_text.lower()) if word.isalpha() and word not in stop_words])
        text_features = tfidf_vectorizer.transform([clean_text])
        
        analyzer = SentimentIntensityAnalyzer()
        sentiment = analyzer.polarity_scores(post_text)['compound']
        
        # Create feature vector
        features = pd.concat([
            pd.DataFrame(text_features.toarray()),
            pd.DataFrame({
                'sentiment_score': [sentiment],
                'word_count': [len(post_text.split())],
                'has_hashtag': ['#' in post_text],
                'has_media': [False]  # Assume no media for input
            })
        ], axis=1)
        features.columns = features.columns.astype(str)
        
        # Predict engagement
        predicted_engagement = engagement_model.predict(features)[0]
        st.write(f"**Predicted Engagement (Likes + Reposts + 0.5 * Replies):** {predicted_engagement:.1f}")
        
        # Suggestions
        suggestions = suggest_diversity_post_content(post_text, predicted_engagement)
        if suggestions:
            st.subheader("Tips to Boost Engagement:")
            for tip in suggestions:
                st.write(f"- {tip}")
        else:
            st.write("Looks good! This post is likely to perform well.")
    else:
        st.write("Please enter a post to analyze!")
