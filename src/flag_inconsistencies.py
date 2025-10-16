import pandas as pd

# Path to your labeled dataset
DATASET_PATH = 'data/cleaned_women_in_ai_posts.csv'

# The columns to check for missing values
REQUIRED_COLUMNS = ['text', 'theme']
# Allowed annotation values
ALLOWED_THEMES = {'AI ethics', 'Event', 'Diversity'}

def flag_inconsistencies(df):
    issues = []
    for idx, row in df.iterrows():
        row_issues = []
        # Check for missing required columns
        for col in REQUIRED_COLUMNS:
            if pd.isna(row.get(col)) or str(row.get(col)).strip() == '':
                row_issues.append(f"Missing value in '{col}'")
        # Check for invalid annotation value
        theme_val = str(row.get('theme')).strip()
        if theme_val and theme_val not in ALLOWED_THEMES:
            row_issues.append(f"Invalid theme '{theme_val}' (allowed: {ALLOWED_THEMES})")
        if row_issues:
            issues.append({'row': idx, 'problems': row_issues, 'row_data': row.to_dict()})
    return issues

if __name__ == "__main__":
    df = pd.read_csv(DATASET_PATH)
    inconsistencies = flag_inconsistencies(df)
    if inconsistencies:
        print(f"Found {len(inconsistencies)} inconsistent rows:\n")
        for issue in inconsistencies:
            print(f"Row {issue['row']}: {issue['problems']}\nData: {issue['row_data']}\n")
    else:
        print("No inconsistencies found. All annotations present and valid.")