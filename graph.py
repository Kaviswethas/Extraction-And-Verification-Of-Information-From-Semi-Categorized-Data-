import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load the JSON file
with open('data.json', 'r') as f:
    data = json.load(f)

# Convert JSON data into DataFrame
# Admin Reports (For the report section)
reports_df = pd.DataFrame(data['reports'])

# Application Form Data (For gender and other details)
application_form_df = pd.DataFrame(data['application_form'])

# Register Data (For user registrations)
register_df = pd.DataFrame(data['register'])

# Admin Details (For admin info)
admin_details_df = pd.DataFrame(data['admin_details'])

# Visual 1: Bar chart of Reports by Admin
plt.figure(figsize=(10, 6))
sns.countplot(x='admin_name', data=reports_df, palette='viridis')
plt.title('Reports Submitted by Each Admin')
plt.xlabel('Admin Name')
plt.ylabel('Number of Reports')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# Visual 2: Gender Distribution in the Application Form (Pie chart)
gender_counts = application_form_df['gender'].value_counts()
plt.figure(figsize=(8, 8))
gender_counts.plot.pie(autopct='%1.1f%%', colors=sns.color_palette('Set2').as_hex(), startangle=90)
plt.title('Gender Distribution of Candidates')
plt.ylabel('')
plt.tight_layout()
plt.show()

# Visual 3: GATE Score Distribution (Histogram)
gate_scores = application_form_df['gate_score'].astype(float)
plt.figure(figsize=(10, 6))
sns.histplot(gate_scores, kde=True, color='skyblue', bins=20)
plt.title('Distribution of GATE Scores')
plt.xlabel('GATE Score')
plt.ylabel('Frequency')
plt.tight_layout()
plt.show()

# Visual 4: Percentage Distribution of Candidates (Bar plot)
application_form_df['percentage'] = application_form_df['percentage'].astype(float)
plt.figure(figsize=(10, 6))
sns.barplot(x=application_form_df['candidate_name'], y=application_form_df['percentage'], palette='Blues')
plt.title('Percentage Distribution of Candidates')
plt.xlabel('Candidate Name')
plt.ylabel('Percentage')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# Visual 5: Admin Names and Number of Candidates Associated
admin_names = application_form_df['father_name'].value_counts()  # Father name as proxy for admin association
plt.figure(figsize=(10, 6))
sns.barplot(x=admin_names.index, y=admin_names.values, palette='Set1')
plt.title('Number of Candidates Associated with Each Admin')
plt.xlabel('Admin Name (Father Name)')
plt.ylabel('Number of Candidates')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
