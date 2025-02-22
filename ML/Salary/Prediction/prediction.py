"""
Salary Prediction Model - Inference Script
==========================================
Developer ::> Gehan Fernando

This script loads a pre-trained salary prediction model and makes predictions based on user input.
It handles the complete inference pipeline including data preprocessing and salary prediction.

Dependencies:
- joblib: For loading saved model and scaler
- numpy: For numerical operations
- pandas: For data manipulation
- scikit-learn: For data preprocessing (StandardScaler)
"""

import joblib
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

# Step 1: Load the trained model and scaler
# Load the previously trained Linear Regression model
model = joblib.load('./Source/salary.pkl')
# Load the fitted StandardScaler for feature normalization
scaler = joblib.load('./Source/scaler.pkl')

# Step 2: Collect user input
# Prompt user to enter years of experience and convert to float
years_experience = float(input("Enter Years of Experience: "))

# Step 3: Preprocess the input data
# Create a DataFrame with the input value (required format for scaler)
input_data = pd.DataFrame([[years_experience]], columns=['years_experience'])
# Scale the input using the same scaler used during training
# This ensures consistency with the training data preprocessing
scaled_input = pd.DataFrame(scaler.transform(input_data), columns=['years_experience'])

# Step 4: Generate prediction
# Use the loaded model to predict salary based on scaled input
predicted_salary = model.predict(scaled_input)

# Step 5: Format and display results
# Print the predicted salary with proper formatting:
# - Use thousands separator
# - Display 2 decimal places
# - Include dollar sign and years of experience
print(f"Predicted Salary for {years_experience} years of experience: ${predicted_salary[0]:,.2f}")
