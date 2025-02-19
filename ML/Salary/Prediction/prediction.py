# Developer ::> Gehan Fernando
import joblib
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

# Step 1: Load the trained model
model = joblib.load('./Source/salary.pkl')
scaler = joblib.load('./Source/scaler.pkl')

# Step 2: Get user input (YearsExperience)
years_experience = float(input("Enter Years of Experience: "))

# Step 3: Prepare the input for prediction
input_data = pd.DataFrame([[years_experience]], columns=['years_experience'])  # Fixed column name
scaled_input = pd.DataFrame(scaler.transform(input_data), columns=['years_experience'])

# Step 4: Predict the Salary using the trained model
predicted_salary = model.predict(scaled_input)

# Step 5: Display the result to the user
print(f"Predicted Salary for {years_experience} years of experience: ${predicted_salary[0]:,.2f}")
