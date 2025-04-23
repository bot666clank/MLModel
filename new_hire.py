import pandas as pd
import random

# Define sample departments and job titles
departments = ['Computer Science', 'Biology', 'Physics', 'Chemistry', 'Mathematics', 'Engineering', 'History', 'Philosophy', 'Art', 'Economics']
job_titles = ['Professor', 'Associate Professor', 'Assistant Professor', 'Lab Assistant', 'Research Assistant', 'IT Support', 'Peer Tutor', 'Tutor', 'Administrative Assistant', 'Library Assistant']

# Define sample statuses
statuses = ['Faculty', 'Staff', 'Undergraduate Student']

# Generate mock data for 50 new hires
new_hires_data = []

for i in range(50):
    name = f"Employee {i+1}"
    uin = random.randint(100000000, 999999999)  # Random 9-digit UIN
    status = random.choice(statuses)
    job_title = random.choice(job_titles)
    department = random.choice(departments)
    hire_year = 2025  # All hires are in 2025
    
    new_hires_data.append([name, uin, status, job_title, department, hire_year])

# Create a DataFrame
new_hires_df = pd.DataFrame(new_hires_data, columns=['Name', 'UIN', 'Status', 'Job Title', 'Department', 'Hire Year'])

# Save to a CSV file
new_hires_df.to_csv('newhire.csv', index=False)

# Output message
print("Generated 50 new hires and saved to 'new_hires_mock_data.csv'.")
