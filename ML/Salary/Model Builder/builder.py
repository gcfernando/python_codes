"""
Salary Prediction Model using Linear Regression
===============================================
Developer ::> Gehan Fernando

This script implements a machine learning pipeline to predict salaries based on years of experience.
It includes data preprocessing, model training, evaluation, and model persistence steps.

Dependencies:
- pandas: For data manipulation and analysis
- scikit-learn: For machine learning algorithms and preprocessing
- joblib: For model persistence
"""

import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
import joblib

# Step 1: Load Data
# Read the salary dataset from CSV file
dataFrame = pd.read_csv("./Source/Salary.csv")

# Step 2: Check and Remove Duplicates
# Count duplicate rows in the dataset
duplicate_count = dataFrame.duplicated().sum()
if duplicate_count > 0:
    # Remove duplicate rows if any exist
    dataFrame.drop_duplicates(inplace=True)
    # Reset index after removing duplicates to maintain continuous indexing
    dataFrame.reset_index(drop=True, inplace=True)

# Step 3: Handle Missing Values
# Calculate threshold for column removal (50% of data length)
threshold = int(0.5 * len(dataFrame))
# Drop columns with more than 50% missing values
dataFrame = dataFrame.dropna(axis=1, thresh=threshold)
# Fill remaining missing values with mean of respective columns
dataFrame.fillna(dataFrame.mean(numeric_only=True), inplace=True)

# Step 4: Feature Scaling
# Initialize StandardScaler for normalizing features
scaler = StandardScaler()
# Standardize 'years_experience' column (mean=0, std=1)
dataFrame[['years_experience']] = scaler.fit_transform(dataFrame[['years_experience']])

# Step 5: Prepare Data for Training
# Select feature (X) and target variable (y)
X = dataFrame[['years_experience']]  # Independent variable
y = dataFrame['salary']              # Dependent variable

# Step 6: Split Data
# Create training and testing sets (80% training, 20% testing)
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,    # 20% of data for testing
    random_state=42   # Set seed for reproducibility
)

# Step 7: Model Training
# Initialize and train Linear Regression model
model = LinearRegression()
model.fit(X_train, y_train)  # Train model on training data

# Step 8: Make Predictions
# Generate predictions on test set
y_pred = model.predict(X_test)

# Step 9: Model Evaluation
# Calculate R-squared score (coefficient of determination)
r2 = r2_score(y_test, y_pred)
# Calculate Mean Squared Error
mse = mean_squared_error(y_test, y_pred)

# Print model performance metric
print(f"R² Score: {r2:.4f}")
print(f"Mean Squared Error: {mse:.2f}")

# Step 10: Model Persistence
# Save model and scaler if R² score meets threshold
if r2 > 0.95:  # 95% accuracy threshold
    # Save the scaler for future data preprocessing
    joblib.dump(scaler, './Source/scaler.pkl')
    # Save the trained model
    joblib.dump(model, './Source/salary.pkl')
    print("Model saved!")
else:
    print("Model not saved as R² score is below 95%.")
