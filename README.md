Hi! This project predicts system permissions for new hires using historical employee data. The goal is to make access provisioning a little smarter and more consistent by learning from how similar roles have been set up in the past.
It combines a multi-label classification model with some fallback logic based on role similarity, so it still works even when the data is messy or incomplete.

What it does
- Predicts permissions for new hires based on role, department, and status
- Groups similar roles and uses those patterns to guide recommendations
- Falls back to fuzzy matching when the model is unsure
- Shows how common each permission is among similar employees (helps spot unusual access)

Input: Historical data (CSV) which contains (Status, Job Title, Department, Hire Year, Permissions)
<img width="659" height="367" alt="Screenshot 2026-04-22 at 12 28 04 AM" src="https://github.com/user-attachments/assets/f739e44d-6098-4882-a7f4-1731586f9456" />

Output: Adds a Recommended Permissions column with a list of predicted access for each new hire.
<img width="639" height="432" alt="Screenshot 2026-04-22 at 12 29 30 AM" src="https://github.com/user-attachments/assets/bc02e1b1-9260-4495-bbb4-277a2b92f1e4" />

Tools used: Python, pandas, scikit-learn (Random Forest, MultiOutputClassifier), basic NLP-style fuzzy matching
