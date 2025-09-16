import pandas as pd

# Read .xls file, skipping metadata row (index 0) and using row 1 as header
df = pd.read_excel('data/linkedin_analytics.xls', skiprows=1, header=0)

# Map LinkedIn columns to required format
df = df.rename(columns={
    'Reactions (organic)': 'likes',    # Map to likes
    'Reposts (organic)': 'reposts',    # Map to reposts
    'Comments (organic)': 'replies',   # Map to replies
    'Date': 'timestamp'                # Map to timestamp
})

# Add placeholder columns for text and has_media
df['text'] = ''  # Will be filled manually
df['has_media'] = False  # Will be filled manually

# Convert timestamp to YYYY-MM-DD HH:MM:SS format
try:
    df['timestamp'] = pd.to_datetime(df['timestamp'], format='%m/%d/%Y').dt.strftime('%Y-%m-%d %H:%M:%S')
except:
    df['timestamp'] = pd.to_datetime(df['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')

# Select only required columns
df = df[['text', 'likes', 'reposts', 'replies', 'timestamp', 'has_media']]

# Save to CSV
df.to_csv('data/linkedin_women_in_ai_posts.csv', index=False)
print("Converted linkedin_analytics.xls to linkedin_women_in_ai_posts.csv! Add post content and has_media manually.")
