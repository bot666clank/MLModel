










# from flask import Flask, render_template, request
# import pandas as pd
# from sklearn.preprocessing import MultiLabelBinarizer
# from sklearn.ensemble import RandomForestClassifier
# from sklearn.multioutput import MultiOutputClassifier
# from sklearn.pipeline import Pipeline
# from sklearn.compose import ColumnTransformer
# from sklearn.model_selection import train_test_split
# from sklearn.preprocessing import OneHotEncoder
# import difflib
# import re

# app = Flask(__name__)

# # === STEP 1: Load the data ===
# historical_df = pd.read_csv("university_permissions_full_2000.csv")
# new_hires_df = pd.read_csv("newhire.csv")

# # === STEP 2: Prepare the model as before ===
# df_grouped = historical_df.groupby(
#     ['Status', 'Job Title', 'Department', 'Hire Year']
# )['Permissions'].apply(list).reset_index()

# X = df_grouped[['Status', 'Job Title', 'Department', 'Hire Year']]
# y = df_grouped['Permissions']

# mlb = MultiLabelBinarizer()
# y_bin = mlb.fit_transform(y)

# categorical_features = ['Status', 'Job Title', 'Department']
# preprocessor = ColumnTransformer(
#     transformers=[('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)],
#     remainder='passthrough'
# )

# model = Pipeline(steps=[
#     ('preprocessor', preprocessor),
#     ('classifier', MultiOutputClassifier(RandomForestClassifier(random_state=42)))
# ])

# X_train, X_test, y_train, y_test = train_test_split(X, y_bin, test_size=0.2, random_state=42)
# model.fit(X_train, y_train)

# # === Helper Functions ===
# def clean_title(title):
#     return re.sub(r'[^\w\s]', '', str(title).lower().strip())

# def fuzzy_match_job_title(new_title, historical_titles):
#     cleaned_new = clean_title(new_title)
#     cleaned_hist = [clean_title(t) for t in historical_titles]
#     matches = difflib.get_close_matches(cleaned_new, cleaned_hist, n=1, cutoff=0.6)
#     if matches:
#         index = cleaned_hist.index(matches[0])
#         return historical_titles[index]
#     return None

# def find_similar_roles(new_hire_row):
#     department, status, job_title = new_hire_row['Department'], new_hire_row['Status'], new_hire_row['Job Title']
#     try:
#         filtered_df = historical_df.loc[(department, status)]
#     except KeyError:
#         return []

#     # 1. Exact match by job title
#     exact_matches = filtered_df[filtered_df['Job Title'].str.lower() == job_title.lower()]
#     if not exact_matches.empty:
#         return list(exact_matches['Permissions'].unique())

#     # 2. Substring match
#     substring_matches = filtered_df[filtered_df['Job Title'].str.contains(job_title, case=False, na=False)]
#     if not substring_matches.empty:
#         return list(substring_matches['Permissions'].unique())

#     # 3. Fuzzy match
#     best_match_title = fuzzy_match_job_title(job_title, filtered_df['Job Title'].dropna().unique())
#     if best_match_title:
#         fuzzy_matches = filtered_df[filtered_df['Job Title'] == best_match_title]
#         return list(fuzzy_matches['Permissions'].unique())

#     return []

# def get_similar_people_access_stats(new_hire_row):
#     job_title = new_hire_row['Job Title']
#     department = new_hire_row['Department']

#     dept_df = historical_df.reset_index()
#     dept_df = dept_df[dept_df['Department'] == department]

#     historical_titles = dept_df['Job Title'].dropna().unique()
#     close_matches = difflib.get_close_matches(job_title, historical_titles, n=5, cutoff=0.5)

#     if not close_matches:
#         return {}

#     similar_people_df = dept_df[dept_df['Job Title'].isin(close_matches)]
#     total_similar_users = similar_people_df['UIN'].nunique()

#     if total_similar_users == 0:
#         return {}

#     permission_counts = (
#         similar_people_df
#         .groupby('Permissions')['UIN']
#         .nunique()
#         .reset_index(name='count')
#     )

#     permission_stats = {
#         row['Permissions']: (row['count'] / total_similar_users) * 100
#         for _, row in permission_counts.iterrows()
#     }

#     return permission_stats

# # === Route for displaying the form and handling submissions ===
# @app.route('/', methods=['GET', 'POST'])
# def index():
#     if request.method == 'POST':
#         name = request.form['Name']
#         uin = request.form['UIN']
#         status = request.form['Status']
#         job_title = request.form['JobTitle']
#         department = request.form['Department']
#         hire_year = request.form['HireYear']
        
#         new_hire_data = pd.DataFrame([{
#             'Name': name,
#             'UIN': uin,
#             'Status': status,
#             'Job Title': job_title,
#             'Department': department,
#             'Hire Year': hire_year
#         }])

#         X_new = new_hire_data[['Status', 'Job Title', 'Department', 'Hire Year']]

#         # Predict permissions using the trained model
#         predictions = model.predict(X_new)

#         predicted_permissions = mlb.inverse_transform(predictions)

#         # Get match percentages for each predicted permission
#         fuzzy_access_stats = get_similar_people_access_stats(new_hire_data.iloc[0])

#         permissions_with_stats = [
#             {'permission': perm, 'percentage': fuzzy_access_stats.get(perm, 0)}
#             for perm in predicted_permissions[0]
#         ]

#         return render_template('index.html', 
#                                permissions_with_stats=permissions_with_stats,
#                                name=name, 
#                                uin=uin)

#     return render_template('index.html', permissions_with_stats=None)

# if __name__ == '__main__':
#     app.run(debug=True)


# from flask import Flask, render_template, request
# import pandas as pd
# from sklearn.preprocessing import MultiLabelBinarizer
# from sklearn.ensemble import RandomForestClassifier
# from sklearn.multioutput import MultiOutputClassifier
# from sklearn.pipeline import Pipeline
# from sklearn.compose import ColumnTransformer
# from sklearn.model_selection import train_test_split
# from sklearn.preprocessing import OneHotEncoder
# import difflib
# import re

# app = Flask(__name__)

# # === STEP 1: Load the data ===
# historical_df = pd.read_csv("university_permissions_full_2000.csv")
# new_hires_df = pd.read_csv("newhire.csv")

# # === STEP 2: Prepare the model as before ===
# # Group historical data by employee profile
# df_grouped = historical_df.groupby(
#     ['Status', 'Job Title', 'Department', 'Hire Year']
# )['Permissions'].apply(list).reset_index()

# X = df_grouped[['Status', 'Job Title', 'Department', 'Hire Year']]
# y = df_grouped['Permissions']

# mlb = MultiLabelBinarizer()
# y_bin = mlb.fit_transform(y)

# categorical_features = ['Status', 'Job Title', 'Department']
# preprocessor = ColumnTransformer(
#     transformers=[('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)],
#     remainder='passthrough'
# )

# model = Pipeline(steps=[
#     ('preprocessor', preprocessor),
#     ('classifier', MultiOutputClassifier(RandomForestClassifier(random_state=42)))
# ])

# X_train, X_test, y_train, y_test = train_test_split(X, y_bin, test_size=0.2, random_state=42)
# model.fit(X_train, y_train)

# # === Helper Functions ===
# def clean_title(title):
#     return re.sub(r'[^\w\s]', '', str(title).lower().strip())

# def fuzzy_match_job_title(new_title, historical_titles):
#     cleaned_new = clean_title(new_title)
#     cleaned_hist = [clean_title(t) for t in historical_titles]
#     matches = difflib.get_close_matches(cleaned_new, cleaned_hist, n=1, cutoff=0.6)
#     if matches:
#         index = cleaned_hist.index(matches[0])
#         return historical_titles[index]
#     return None

# def find_similar_roles(new_hire_row):
#     department, status, job_title = new_hire_row['Department'], new_hire_row['Status'], new_hire_row['Job Title']
#     filtered_df = historical_df.loc[(department, status)]
#     exact_matches = filtered_df[filtered_df['Job Title'].str.lower() == job_title.lower()]
#     if not exact_matches.empty:
#         return list(exact_matches['Permissions'].unique())

#     substring_matches = filtered_df[filtered_df['Job Title'].str.contains(job_title, case=False, na=False)]
#     if not substring_matches.empty:
#         return list(substring_matches['Permissions'].unique())

#     best_match_title = fuzzy_match_job_title(job_title, filtered_df['Job Title'].dropna().unique())
#     if best_match_title:
#         fuzzy_matches = filtered_df[filtered_df['Job Title'] == best_match_title]
#         return list(fuzzy_matches['Permissions'].unique())

#     return []

# def get_similar_people_access_stats(new_hire_row):
#     job_title = new_hire_row['Job Title']
#     department = new_hire_row['Department']

#     # Only use people from the same department (you could remove this restriction if needed)
#     dept_df = historical_df.reset_index()
#     dept_df = dept_df[dept_df['Department'] == department]

#     historical_titles = dept_df['Job Title'].dropna().unique()
#     close_matches = difflib.get_close_matches(job_title, historical_titles, n=5, cutoff=0.5)

#     if not close_matches:
#         return {}

#     similar_people_df = dept_df[dept_df['Job Title'].isin(close_matches)]
#     total_similar_users = similar_people_df['UIN'].nunique()

#     if total_similar_users == 0:
#         return {}

#     # Count how many similar users had each permission
#     permission_counts = (
#         similar_people_df
#         .groupby('Permissions')['UIN']
#         .nunique()
#         .reset_index(name='count')
#     )

#     # Calculate percentage of similar users with each permission
#     permission_stats = {
#         row['Permissions']: (row['count'] / total_similar_users) * 100
#         for _, row in permission_counts.iterrows()
#     }

#     return permission_stats

# # === Route for displaying the form and handling submissions ===
# @app.route('/', methods=['GET', 'POST'])
# def index():
#     if request.method == 'POST':
#         # Extract user input from the form
#         name = request.form['Name']
#         uin = request.form['UIN']
#         status = request.form['Status']
#         job_title = request.form['JobTitle']
#         department = request.form['Department']
#         hire_year = request.form['HireYear']
        
#         # Create new hire DataFrame for this submission
#         new_hire_data = pd.DataFrame([{
#             'Name': name,
#             'UIN': uin,
#             'Status': status,
#             'Job Title': job_title,
#             'Department': department,
#             'Hire Year': hire_year
#         }])

#         # Prepare input for model prediction
#         X_new = new_hire_data[['Status', 'Job Title', 'Department', 'Hire Year']]

#         # Predict permissions using the trained model
#         predictions = model.predict(X_new)

#         # Decode the predicted binary labels back into permission names
#         predicted_permissions = mlb.inverse_transform(predictions)

#         # Get match percentages for each predicted permission
#         fuzzy_access_stats = get_similar_people_access_stats(new_hire_data.iloc[0])

#         # Prepare permission data with match percentages
#         permissions_with_stats = [
#             {'permission': perm, 'percentage': fuzzy_access_stats.get(perm, 0)}
#             for perm in predicted_permissions[0]
#         ]

#         # Return the result to the user
#         return render_template('index.html', 
#                                permissions_with_stats=permissions_with_stats,
#                                name=name, 
#                                uin=uin)

#     # Default view for GET request (empty form)
#     return render_template('index.html', permissions_with_stats=None)

# if __name__ == '__main__':
#     app.run(debug=True)

# from flask import Flask, render_template, request
# import pandas as pd
# from sklearn.preprocessing import MultiLabelBinarizer
# from sklearn.ensemble import RandomForestClassifier
# from sklearn.multioutput import MultiOutputClassifier
# from sklearn.pipeline import Pipeline
# from sklearn.compose import ColumnTransformer
# from sklearn.model_selection import train_test_split
# from sklearn.preprocessing import OneHotEncoder
# import difflib
# import re

# app = Flask(__name__)

# # === STEP 1: Load the data ===
# historical_df = pd.read_csv("university_permissions_full_2000.csv")
# new_hires_df = pd.read_csv("newhire.csv")

# # === STEP 2: Prepare the model as before ===
# # Group historical data by employee profile
# df_grouped = historical_df.groupby(
#     ['Status', 'Job Title', 'Department', 'Hire Year']
# )['Permissions'].apply(list).reset_index()

# X = df_grouped[['Status', 'Job Title', 'Department', 'Hire Year']]
# y = df_grouped['Permissions']

# mlb = MultiLabelBinarizer()
# y_bin = mlb.fit_transform(y)

# categorical_features = ['Status', 'Job Title', 'Department']
# preprocessor = ColumnTransformer(
#     transformers=[('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)],
#     remainder='passthrough'
# )

# model = Pipeline(steps=[
#     ('preprocessor', preprocessor),
#     ('classifier', MultiOutputClassifier(RandomForestClassifier(random_state=42)))
# ])

# X_train, X_test, y_train, y_test = train_test_split(X, y_bin, test_size=0.2, random_state=42)
# model.fit(X_train, y_train)

# # === Helper Functions ===
# def clean_title(title):
#     return re.sub(r'[^\w\s]', '', str(title).lower().strip())

# def fuzzy_match_job_title(new_title, historical_titles):
#     cleaned_new = clean_title(new_title)
#     cleaned_hist = [clean_title(t) for t in historical_titles]
#     matches = difflib.get_close_matches(cleaned_new, cleaned_hist, n=1, cutoff=0.6)
#     if matches:
#         index = cleaned_hist.index(matches[0])
#         return historical_titles[index]
#     return None

# def find_similar_roles(new_hire_row):
#     department, status, job_title = new_hire_row['Department'], new_hire_row['Status'], new_hire_row['Job Title']
#     filtered_df = historical_df.loc[(department, status)]
#     exact_matches = filtered_df[filtered_df['Job Title'].str.lower() == job_title.lower()]
#     if not exact_matches.empty:
#         return list(exact_matches['Permissions'].unique())

#     substring_matches = filtered_df[filtered_df['Job Title'].str.contains(job_title, case=False, na=False)]
#     if not substring_matches.empty:
#         return list(substring_matches['Permissions'].unique())

#     best_match_title = fuzzy_match_job_title(job_title, filtered_df['Job Title'].dropna().unique())
#     if best_match_title:
#         fuzzy_matches = filtered_df[filtered_df['Job Title'] == best_match_title]
#         return list(fuzzy_matches['Permissions'].unique())

#     return []

# # === Route for displaying the form and handling submissions ===
# # @app.route('/', methods=['GET', 'POST'])
# # def index():
# #     if request.method == 'POST':
# #         # Extract user input from the form
# #         name = request.form['Name']
# #         uin = request.form['UIN']
# #         status = request.form['Status']
# #         job_title = request.form['JobTitle']
# #         department = request.form['Department']
# #         hire_year = request.form['HireYear']
        
# #         # Create new hire DataFrame for this submission
# #         new_hire_data = pd.DataFrame([{
# #             'Name': name,
# #             'UIN': uin,
# #             'Status': status,
# #             'Job Title': job_title,
# #             'Department': department,
# #             'Hire Year': hire_year
# #         }])

# #         # Prepare input for model prediction
# #         X_new = new_hire_data[['Status', 'Job Title', 'Department', 'Hire Year']]

# #         # Predict permissions using the trained model
# #         predictions = model.predict(X_new)

# #         # Decode the predicted binary labels back into permission names
# #         predicted_permissions = mlb.inverse_transform(predictions)

# #         # Return the result to the user
# #         return render_template('index.html', 
# #                                predicted_permissions=predicted_permissions[0],
# #                                name=name, 
# #                                uin=uin)

# #     # Default view for GET request (empty form)
# #     return render_template('index.html', predicted_permissions=None)
# @app.route('/', methods=['GET', 'POST'])
# def index():
#     if request.method == 'POST':
#         # Extract user input from the form
#         name = request.form['Name']
#         uin = request.form['UIN']
#         status = request.form['Status']
#         job_title = request.form['JobTitle']
#         department = request.form['Department']
#         hire_year = request.form['HireYear']
        
#         # Create new hire DataFrame for this submission
#         new_hire_data = pd.DataFrame([{
#             'Name': name,
#             'UIN': uin,
#             'Status': status,
#             'Job Title': job_title,
#             'Department': department,
#             'Hire Year': hire_year
#         }])

#         # Prepare input for model prediction
#         X_new = new_hire_data[['Status', 'Job Title', 'Department', 'Hire Year']]

#         # Predict permissions using the trained model
#         predictions = model.predict(X_new)

#         # Decode the predicted binary labels back into permission names
#         predicted_permissions = mlb.inverse_transform(predictions)

#         # Get match percentages for each predicted permission
#         fuzzy_access_stats = get_similar_people_access_stats(new_hire_data.iloc[0])

#         # Prepare permission data with match percentages
#         permissions_with_stats = [
#             {'permission': perm, 'percentage': fuzzy_access_stats.get(perm, 0)}
#             for perm in predicted_permissions[0]
#         ]

#         # Return the result to the user
#         return render_template('index.html', 
#                                permissions_with_stats=permissions_with_stats,
#                                name=name, 
#                                uin=uin)

#     # Default view for GET request (empty form)
#     return render_template('index.html', permissions_with_stats=None)

# if __name__ == '__main__':
#     app.run(debug=True)


# from flask import Flask, render_template_string, request
# import pandas as pd
# from sklearn.preprocessing import MultiLabelBinarizer, OneHotEncoder
# from sklearn.model_selection import train_test_split
# from sklearn.ensemble import RandomForestClassifier
# from sklearn.multioutput import MultiOutputClassifier
# from sklearn.pipeline import Pipeline
# from sklearn.compose import ColumnTransformer
# import difflib
# import re

# app = Flask(__name__)

# # === Load and Prepare Data ===
# historical_df = pd.read_csv("university_permissions_full_2000.csv")
# new_hires_df = pd.read_csv("newhire.csv")

# df_grouped = historical_df.groupby(['Status', 'Job Title', 'Department', 'Hire Year'])['Permissions'].apply(list).reset_index()
# X = df_grouped[['Status', 'Job Title', 'Department', 'Hire Year']]
# y = df_grouped['Permissions']

# mlb = MultiLabelBinarizer()
# y_bin = mlb.fit_transform(y)

# categorical_features = ['Status', 'Job Title', 'Department']
# preprocessor = ColumnTransformer(
#     transformers=[('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)],
#     remainder='passthrough'
# )

# model = Pipeline(steps=[
#     ('preprocessor', preprocessor),
#     ('classifier', MultiOutputClassifier(RandomForestClassifier(random_state=42)))
# ])

# X_train, X_test, y_train, y_test = train_test_split(X, y_bin, test_size=0.2, random_state=42)
# model.fit(X_train, y_train)

# historical_df['Role'] = historical_df[['Status', 'Job Title', 'Department']].astype(str).agg(' | '.join, axis=1)
# historical_df.set_index(['Department', 'Status'], inplace=True)
# historical_df.sort_index(inplace=True)

# # === Helper Functions ===

# def clean_title(title):
#     return re.sub(r'[^\w\s]', '', str(title).lower().strip())

# def fuzzy_match_job_title(new_title, historical_titles):
#     cleaned_new = clean_title(new_title)
#     cleaned_hist = [clean_title(t) for t in historical_titles]
#     matches = difflib.get_close_matches(cleaned_new, cleaned_hist, n=1, cutoff=0.6)
#     if matches:
#         index = cleaned_hist.index(matches[0])
#         return historical_titles[index]
#     return None

# def find_similar_roles(new_hire_row):
#     department = new_hire_row['Department']
#     status = new_hire_row['Status']
#     job_title = new_hire_row['Job Title']
    
#     try:
#         filtered_df = historical_df.loc[(department, status)]
#     except KeyError:
#         return []

#     exact_matches = filtered_df[filtered_df['Job Title'].str.lower() == job_title.lower()]
#     if not exact_matches.empty:
#         return list(exact_matches['Permissions'].unique())

#     substring_matches = filtered_df[filtered_df['Job Title'].str.contains(job_title, case=False, na=False)]
#     if not substring_matches.empty:
#         return list(substring_matches['Permissions'].unique())

#     best_match = fuzzy_match_job_title(job_title, filtered_df['Job Title'].dropna().unique())
#     if best_match:
#         fuzzy_matches = filtered_df[filtered_df['Job Title'] == best_match]
#         return list(fuzzy_matches['Permissions'].unique())

#     return []

# def get_similar_people_access_stats(new_hire_row):
#     job_title = new_hire_row['Job Title']
#     department = new_hire_row['Department']

#     dept_df = historical_df.reset_index()
#     dept_df = dept_df[dept_df['Department'] == department]
#     historical_titles = dept_df['Job Title'].dropna().unique()
#     close_matches = difflib.get_close_matches(job_title, historical_titles, n=5, cutoff=0.5)

#     if not close_matches:
#         return {}

#     similar_people_df = dept_df[dept_df['Job Title'].isin(close_matches)]
#     total_similar_users = similar_people_df['UIN'].nunique()
#     if total_similar_users == 0:
#         return {}

#     permission_counts = (
#         similar_people_df
#         .groupby('Permissions')['UIN']
#         .nunique()
#         .reset_index(name='count')
#     )

#     return {
#         row['Permissions']: (row['count'] / total_similar_users) * 100
#         for _, row in permission_counts.iterrows()
#     }

# # === Flask Routes ===

# form_html = """
# <!DOCTYPE html>
# <html>
# <head><title>New Hire Access Predictor</title></head>
# <body>
#     <h2>New Hire Access Form</h2>
#     <form method="POST">
#         Name: <input type="text" name="name" required><br>
#         UIN: <input type="text" name="uin" required><br>
#         Status: <input type="text" name="status" required><br>
#         Job Title: <input type="text" name="job_title" required><br>
#         Department: <input type="text" name="department" required><br>
#         Hire Year: <input type="number" name="hire_year" required><br>
#         <input type="submit" value="Submit">
#     </form>
# </body>
# </html>
# """

# results_html = """
# <!DOCTYPE html>
# <html>
# <head><title>Prediction Results</title></head>
# <body>
#     <h2>Recommendations for {{ name }}</h2>
#     <p><strong>Job Title:</strong> {{ job_title }}</p>
#     <h3>🔐 Recommended Permissions:</h3>
#     {% if permissions %}
#         <ul>
#         {% for perm, percent in permissions %}
#             <li>{{ perm }} — {{ "%.1f"|format(percent) }}% of similar employees had this</li>
#         {% endfor %}
#         </ul>
#     {% else %}
#         <p>No permissions could be recommended.</p>
#     {% endif %}
#     <a href="/">← Back to Form</a>
# </body>
# </html>
# """

# @app.route('/', methods=['GET', 'POST'])
# def index():
#     if request.method == 'POST':
#         name = request.form['name']
#         uin = request.form['uin']
#         status = request.form['status']
#         job_title = request.form['job_title']
#         department = request.form['department']
#         hire_year = int(request.form['hire_year'])

#         input_df = pd.DataFrame([{
#             'Status': status,
#             'Job Title': job_title,
#             'Department': department,
#             'Hire Year': hire_year
#         }])

#         prediction = model.predict(input_df)
#         permissions = mlb.inverse_transform(prediction)[0]

#         if not permissions:
#             permissions = find_similar_roles(input_df.iloc[0])

#         stats = get_similar_people_access_stats(input_df.iloc[0])
#         sorted_perms = sorted(
#             [(perm, stats.get(perm, 0)) for perm in permissions],
#             key=lambda x: x[1], reverse=True
#         )

#         return render_template_string(results_html, name=name, job_title=job_title, permissions=sorted_perms)

#     return render_template_string(form_html)

# # === Run Flask App ===
# if __name__ == '__main__':
#     app.run(debug=True)











