# Import necessary libraries
from flask import Flask, render_template_string, request  # Web app and HTML rendering
import pandas as pd  # For data manipulation
from sklearn.preprocessing import MultiLabelBinarizer, OneHotEncoder  # Encoding labels and categorical features
from sklearn.model_selection import train_test_split  # Split data into train/test
from sklearn.ensemble import RandomForestClassifier  # ML model
from sklearn.multioutput import MultiOutputClassifier  # Handles multilabel classification
from sklearn.pipeline import Pipeline  # To chain preprocessing and modeling
from sklearn.compose import ColumnTransformer  # To apply transformers to specific columns
import difflib  # For fuzzy matching
import re  # Regular expressions for string cleaning

# Initialize Flask application
app = Flask(__name__)

# === Load and Prepare Data ===

# Load historical permissions dataset and new hire data
historical_df = pd.read_csv("university_permissions_full_2000.csv")
new_hires_df = pd.read_csv("newhire.csv")  # This isn't used in the app logic but could be used for testing

# Group permissions by combinations of role attributes and convert permissions to list format
df_grouped = historical_df.groupby(
    ['Status', 'Job Title', 'Department', 'Hire Year']
)['Permissions'].apply(list).reset_index()

# Define features (X) and target (y)
X = df_grouped[['Status', 'Job Title', 'Department', 'Hire Year']]
y = df_grouped['Permissions']

# Convert list of permissions into binary matrix format for multi-label classification
mlb = MultiLabelBinarizer()
y_bin = mlb.fit_transform(y)

# Specify which columns to one-hot encode
categorical_features = ['Status', 'Job Title', 'Department']
preprocessor = ColumnTransformer(
    transformers=[
        ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
    ],
    remainder='passthrough'  # Leave other columns (like 'Hire Year') as-is
)

# Create a pipeline that first preprocesses input, then applies a multi-output random forest classifier
model = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('classifier', MultiOutputClassifier(RandomForestClassifier(random_state=42)))
])

# Split the dataset for training and testing
X_train, X_test, y_train, y_test = train_test_split(X, y_bin, test_size=0.2, random_state=42)

# Train the model
model.fit(X_train, y_train)

# Create a composite role string for fuzzy-matching purposes
historical_df['Role'] = historical_df[['Status', 'Job Title', 'Department']].astype(str).agg(' | '.join, axis=1)

# Reindex the dataframe for faster lookup by (Department, Status)
historical_df.set_index(['Department', 'Status'], inplace=True)
historical_df.sort_index(inplace=True)

# === Helper Functions ===

# Cleans job titles by removing punctuation and converting to lowercase
def clean_title(title):
    return re.sub(r'[^\w\s]', '', str(title).lower().strip())

# Finds the closest job title match using difflib
def fuzzy_match_job_title(new_title, historical_titles):
    cleaned_new = clean_title(new_title)
    cleaned_hist = [clean_title(t) for t in historical_titles]
    matches = difflib.get_close_matches(cleaned_new, cleaned_hist, n=1, cutoff=0.6)
    if matches:
        index = cleaned_hist.index(matches[0])
        return historical_titles[index]
    return None

# Attempts to find similar roles and their permissions when the model doesn't return predictions
def find_similar_roles(new_hire_row):
    department = new_hire_row['Department']
    status = new_hire_row['Status']
    job_title = new_hire_row['Job Title']
    
    # Try to find matching department and status in historical data
    try:
        filtered_df = historical_df.loc[(department, status)]
    except KeyError:
        return []

    # Try exact match first
    exact_matches = filtered_df[filtered_df['Job Title'].str.lower() == job_title.lower()]
    if not exact_matches.empty:
        return list(exact_matches['Permissions'].unique())

    # Try substring match
    substring_matches = filtered_df[filtered_df['Job Title'].str.contains(job_title, case=False, na=False)]
    if not substring_matches.empty:
        return list(substring_matches['Permissions'].unique())

    # Use fuzzy matching as last resort
    best_match = fuzzy_match_job_title(job_title, filtered_df['Job Title'].dropna().unique())
    if best_match:
        fuzzy_matches = filtered_df[filtered_df['Job Title'] == best_match]
        return list(fuzzy_matches['Permissions'].unique())

    return []

# Gathers statistics on how often similar people had each permission
def get_similar_people_access_stats(new_hire_row):
    job_title = new_hire_row['Job Title']
    department = new_hire_row['Department']

    # Flatten index for filtering
    dept_df = historical_df.reset_index()
    dept_df = dept_df[dept_df['Department'] == department]
    historical_titles = dept_df['Job Title'].dropna().unique()

    # Find similar job titles
    close_matches = difflib.get_close_matches(job_title, historical_titles, n=5, cutoff=0.5)
    if not close_matches:
        return {}

    similar_people_df = dept_df[dept_df['Job Title'].isin(close_matches)]
    total_similar_users = similar_people_df['UIN'].nunique()
    if total_similar_users == 0:
        return {}

    # Count how many unique people had each permission
    permission_counts = (
        similar_people_df
        .groupby('Permissions')['UIN']
        .nunique()
        .reset_index(name='count')
    )

    # Convert to percentage
    return {
        row['Permissions']: (row['count'] / total_similar_users) * 100
        for _, row in permission_counts.iterrows()
    }

# === HTML Templates ===

# Simple HTML form for input
form_html = """
<!DOCTYPE html>
<html>
<head><title>New Hire Access Predictor</title></head>
<body>
    <h2>New Hire Access Form</h2>
    <form method="POST">
        Name: <input type="text" name="name" required><br>
        UIN: <input type="text" name="uin" required><br>
        Status: <input type="text" name="status" required><br>
        Job Title: <input type="text" name="job_title" required><br>
        Department: <input type="text" name="department" required><br>
        Hire Year: <input type="number" name="hire_year" required><br>
        <input type="submit" value="Submit">
    </form>
</body>
</html>
"""

# HTML to show predictions
results_html = """
<!DOCTYPE html>
<html>
<head><title>Prediction Results</title></head>
<body>
    <h2>Recommendations for {{ name }}</h2>
    <p><strong>Job Title:</strong> {{ job_title }}</p>
    <h3>🔐 Recommended Permissions:</h3>
    {% if permissions %}
        <ul>
        {% for perm, percent in permissions %}
            <li>{{ perm }} — {{ "%.1f"|format(percent) }}% of similar employees had this</li>
        {% endfor %}
        </ul>
    {% else %}
        <p>No permissions could be recommended.</p>
    {% endif %}
    <a href="/">← Back to Form</a>
</body>
</html>
"""

# === Flask Route ===

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Retrieve form data
        name = request.form['name']
        uin = request.form['uin']
        status = request.form['status']
        job_title = request.form['job_title']
        department = request.form['department']
        hire_year = int(request.form['hire_year'])

        # Create input dataframe for prediction
        input_df = pd.DataFrame([{
            'Status': status,
            'Job Title': job_title,
            'Department': department,
            'Hire Year': hire_year
        }])

        # Predict permissions using trained model
        prediction = model.predict(input_df)
        permissions = mlb.inverse_transform(prediction)[0]

        # If prediction fails or is empty, try matching similar roles manually
        if not permissions:
            permissions = find_similar_roles(input_df.iloc[0])

        # Get statistical context for similar employees
        stats = get_similar_people_access_stats(input_df.iloc[0])
        
        # Sort permissions by frequency of occurrence among similar employees
        sorted_perms = sorted(
            [(perm, stats.get(perm, 0)) for perm in permissions],
            key=lambda x: x[1], reverse=True
        )

        # Render prediction results
        return render_template_string(results_html, name=name, job_title=job_title, permissions=sorted_perms)

    # Render form on GET request
    return render_template_string(form_html)

# === Run App ===
if __name__ == '__main__':
    app.run(debug=True)
