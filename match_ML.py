# Import required libraries
import pandas as pd
from sklearn.preprocessing import MultiLabelBinarizer, OneHotEncoder
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.multioutput import MultiOutputClassifier
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
import difflib  # For fuzzy matching of job titles
import re       # For cleaning job titles

# === STEP 1: Load the data ===

# Load historical employee permissions data
historical_df = pd.read_csv("university_permissions_full_2000.csv")

# Load the new hires data (these people need to be provisioned)
new_hires_df = pd.read_csv("newhire.csv")

# === STEP 2: Prepare data for model training ===

# Group historical data by employee profile to get a list of all permissions they had
df_grouped = historical_df.groupby(
    ['Status', 'Job Title', 'Department', 'Hire Year']
)['Permissions'].apply(list).reset_index()

# Input features (employee profile)
X = df_grouped[['Status', 'Job Title', 'Department', 'Hire Year']]
# Output labels (permissions as multi-label classification)
y = df_grouped['Permissions']

# Convert the permissions list into binary multi-label format
mlb = MultiLabelBinarizer()
y_bin = mlb.fit_transform(y)

# Identify which features are categorical for preprocessing
categorical_features = ['Status', 'Job Title', 'Department']

# Build the preprocessing pipeline (OneHotEncode categorical features, leave numerical as-is)
preprocessor = ColumnTransformer(
    transformers=[('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)],
    remainder='passthrough'
)

# Define full machine learning pipeline
# 1. Preprocess input
# 2. Train multi-output Random Forest (one classifier per permission)
model = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('classifier', MultiOutputClassifier(RandomForestClassifier(random_state=42)))
])

# Split data into training and test sets (not used here, but good practice)
X_train, X_test, y_train, y_test = train_test_split(X, y_bin, test_size=0.2, random_state=42)

# Train the model
model.fit(X_train, y_train)

# === STEP 3: Predict permissions for new hires ===

# Extract new hire input features
X_new = new_hires_df[['Status', 'Job Title', 'Department', 'Hire Year']]

# Predict permissions using the trained model
predictions = model.predict(X_new)

# Decode the predicted binary labels back into permission names
predicted_permissions = mlb.inverse_transform(predictions)

# Save predictions to the new hires DataFrame
new_hires_df['Recommended Permissions'] = predicted_permissions

# === STEP 4: Create role strings (useful for grouping and analysis) ===

# Combine key features to create a unique "Role" string
role_columns = ['Status', 'Job Title', 'Department']
historical_df['Role'] = historical_df[role_columns].astype(str).agg(' | '.join, axis=1)
new_hires_df['Role'] = new_hires_df[role_columns].astype(str).agg(' | '.join, axis=1)

# === STEP 5: Prepare historical data for fuzzy matching ===

# Set a multi-index for fast lookup by Department and Status
historical_df.set_index(['Department', 'Status'], inplace=True)
historical_df.sort_index(inplace=True)  # Avoid performance warnings

# === STEP 6: Helper Functions ===

# Clean job titles by removing punctuation and normalizing case
def clean_title(title):
    return re.sub(r'[^\w\s]', '', str(title).lower().strip())

# Fuzzy match the new hire job title to one of the historical job titles
def fuzzy_match_job_title(new_title, historical_titles):
    cleaned_new = clean_title(new_title)
    cleaned_hist = [clean_title(t) for t in historical_titles]
    matches = difflib.get_close_matches(cleaned_new, cleaned_hist, n=1, cutoff=0.6)
    if matches:
        index = cleaned_hist.index(matches[0])
        return historical_titles[index]
    return None

# Find similar roles (fallback if model prediction fails)
def find_similar_roles(new_hire_row):
    department, status, job_title = new_hire_row['Department'], new_hire_row['Status'], new_hire_row['Job Title']
    try:
        filtered_df = historical_df.loc[(department, status)]
    except KeyError:
        return []

    # 1. Exact match by job title
    exact_matches = filtered_df[filtered_df['Job Title'].str.lower() == job_title.lower()]
    if not exact_matches.empty:
        return list(exact_matches['Permissions'].unique())

    # 2. Substring match
    substring_matches = filtered_df[filtered_df['Job Title'].str.contains(job_title, case=False, na=False)]
    if not substring_matches.empty:
        return list(substring_matches['Permissions'].unique())

    # 3. Fuzzy match
    best_match_title = fuzzy_match_job_title(job_title, filtered_df['Job Title'].dropna().unique())
    if best_match_title:
        fuzzy_matches = filtered_df[filtered_df['Job Title'] == best_match_title]
        return list(fuzzy_matches['Permissions'].unique())

    return []

# Analyze similar people to get % of similar employees with each permission
def get_similar_people_access_stats(new_hire_row):
    job_title = new_hire_row['Job Title']
    department = new_hire_row['Department']

    # Only use people from the same department (you could remove this restriction if needed)
    dept_df = historical_df.reset_index()
    dept_df = dept_df[dept_df['Department'] == department]

    historical_titles = dept_df['Job Title'].dropna().unique()
    close_matches = difflib.get_close_matches(job_title, historical_titles, n=5, cutoff=0.5)

    if not close_matches:
        return {}

    similar_people_df = dept_df[dept_df['Job Title'].isin(close_matches)]
    total_similar_users = similar_people_df['UIN'].nunique()

    if total_similar_users == 0:
        return {}

    # Count how many similar users had each permission
    permission_counts = (
        similar_people_df
        .groupby('Permissions')['UIN']
        .nunique()
        .reset_index(name='count')
    )

    # Calculate percentage of similar users with each permission
    permission_stats = {
        row['Permissions']: (row['count'] / total_similar_users) * 100
        for _, row in permission_counts.iterrows()
    }

    return permission_stats

# === STEP 7: Fallback recommendations for new hires with empty predictions ===

for idx, row in new_hires_df.iterrows():
    if not row['Recommended Permissions']:
        similar_permissions = find_similar_roles(row)
        new_hires_df.at[idx, 'Recommended Permissions'] = similar_permissions

# === STEP 8: Display predicted permissions summary ===
print("🔮 Predicted Permissions for New Hires:")
print(new_hires_df[['Name', 'Job Title', 'Recommended Permissions']])

# === STEP 9: Interactive lookup for HR, managers, etc. ===

while True:
    print("\n🔍 Enter a new hire's name to view app recommendations and match confidence (or type 'exit' to quit):")
    user_input = input("Name: ").strip()

    if user_input.lower() == "exit":
        print("Exiting. Have a great day! 👋")
        break

    if user_input in new_hires_df['Name'].values:
        row = new_hires_df[new_hires_df['Name'] == user_input].iloc[0]
        apps = row['Recommended Permissions']

        print(f"\n👤 New Hire: {row['Name']} | Role: {row['Role']}")
        print("🔐 Recommended Applications Based on Similar Roles:")

        fuzzy_access_stats = get_similar_people_access_stats(row)

        if not apps:
            print(" - No recommendations available.")
        else:
            # Sort by match percentage
            apps_sorted = sorted(apps, key=lambda app: fuzzy_access_stats.get(app, 0), reverse=True)
            for app in apps_sorted:
                percent = fuzzy_access_stats.get(app, 0)
                marker = "❗" if percent < 10 else ""
                print(f" - {app}  ➜  {percent:.1f}% of similar employees had access {marker}")
    else:
        print("⚠️ Name not found in new hires list. Please try again.")
