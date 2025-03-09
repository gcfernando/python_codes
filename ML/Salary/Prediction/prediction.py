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
def load_model_and_scaler(model_path, scaler_path):
    """
    Loads the pre-trained model and scaler from the given file paths.

    Args:
    - model_path (str): Path to the saved model file.
    - scaler_path (str): Path to the saved scaler file.

    Returns:
    - model (LinearRegression): Loaded trained model.
    - scaler (StandardScaler): Loaded fitted scaler.
    """
    model = joblib.load(model_path)
    scaler = joblib.load(scaler_path)
    return model, scaler

# Step 2: Collect user input
def collect_user_input():
    """
    Prompts the user to enter years of experience.

    Returns:
    - float: User input for years of experience.
    """
    years_experience = float(input("Enter Years of Experience: "))
    return years_experience

# Step 3: Preprocess the input data
def preprocess_input_data(years_experience, scaler):
    """
    Preprocesses the user's input data (scales the years of experience).

    Args:
    - years_experience (float): The years of experience input by the user.
    - scaler (StandardScaler): The fitted scaler for data normalization.

    Returns:
    - scaled_input (DataFrame): Scaled version of the user input.
    """
    # Create a DataFrame with the input value (required format for scaler)
    input_data = pd.DataFrame([[years_experience]], columns=['years_experience'])

    # Scale the input using the same scaler used during training
    scaled_input = pd.DataFrame(scaler.transform(input_data), columns=['years_experience'])
    return scaled_input

# Step 4: Generate prediction
def generate_prediction(model, scaled_input):
    """
    Generates a salary prediction based on the scaled user input.

    Args:
    - model (LinearRegression): The trained model.
    - scaled_input (DataFrame): Scaled input data for prediction.

    Returns:
    - predicted_salary (float): The predicted salary.
    """
    predicted_salary = model.predict(scaled_input)
    return predicted_salary

# Step 5: Format and display results
def display_results(years_experience, predicted_salary):
    """
    Displays the predicted salary with proper formatting.

    Args:
    - years_experience (float): The input years of experience.
    - predicted_salary (float): The predicted salary based on the input.
    """
    # Print the predicted salary with proper formatting:
    # - Use thousands separator
    # - Display 2 decimal places
    # - Include dollar sign and years of experience
    print(f"Predicted Salary for {years_experience} years of experience: ${predicted_salary[0]:,.2f}")

# Main function to execute the inference pipeline
def main():
    # Step 1: Load the pre-trained model and scaler
    model, scaler = load_model_and_scaler('./Source/salary.pkl', './Source/scaler.pkl')

    # Step 2: Collect user input
    years_experience = collect_user_input()

    # Step 3: Preprocess the input data
    scaled_input = preprocess_input_data(years_experience, scaler)

    # Step 4: Generate prediction
    predicted_salary = generate_prediction(model, scaled_input)

    # Step 5: Format and display results
    display_results(years_experience, predicted_salary)

# Run the main function
if __name__ == "__main__":
    main()
