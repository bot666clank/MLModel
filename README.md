Hi! I built this using Python with pandas and scikit-learn, using one-hot encoding for preprocessing and a Random Forest with a MultiOutputClassifier for multi-label prediction. I also added a fallback layer with simple fuzzy matching to handle inconsistent job titles and edge cases where the model has low confidence. The pipeline reads in CSV data, processes employee features, and outputs recommended permissions along with some lightweight confidence signals. Most of the work went into making the system robust to messy, real-world data while keeping the results easy to interpret!

What it does
- Predicts permissions for new hires based on role, department, and status
- Groups similar roles and uses those patterns to guide recommendations
- Shows how common each permission is among similar employees (helps spot unusual access)

Input: Historical data (CSV) which contains (Status, Job Title, Department, Hire Year, Permissions)
<img width="659" height="367" alt="Screenshot 2026-04-22 at 12 28 04 AM" src="https://github.com/user-attachments/assets/f739e44d-6098-4882-a7f4-1731586f9456" />




Output: Adds a Recommended Permissions column with a list of predicted access for each new hire.
<img width="639" height="432" alt="Screenshot 2026-04-22 at 12 29 30 AM" src="https://github.com/user-attachments/assets/bc02e1b1-9260-4495-bbb4-277a2b92f1e4" />




Tools used: Python, pandas, scikit-learn (Random Forest, MultiOutputClassifier), basic NLP-style fuzzy matching
