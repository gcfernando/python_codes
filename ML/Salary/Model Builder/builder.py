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

# Method 1: Load Dataset
def load_data(file_path):
    """
    Load the dataset from the given file path.

    Args:
    - file_path (str): Path to the CSV file containing the dataset.

    Returns:
    - DataFrame: Loaded dataset.
    """
    return pd.read_csv(file_path)

# Method 2: Remove Duplicates
def remove_duplicates(dataFrame):
    """
    Removes duplicate rows from the dataset.

    Args:
    - dataFrame (DataFrame): The input dataset.

    Returns:
    - DataFrame: Dataset with duplicates removed.
    """
    duplicate_count = dataFrame.duplicated().sum()
    if duplicate_count > 0:
        dataFrame.drop_duplicates(inplace=True)
        dataFrame.reset_index(drop=True, inplace=True)
    return dataFrame

# Method 3: Handle Missing Values
def handle_missing_values(dataFrame):
    """
    Handles missing values in the dataset by:
    - Dropping columns with more than 50% missing values.
    - Filling remaining missing values with column mean.

    Args:
    - dataFrame (DataFrame): The input dataset.

    Returns:
    - DataFrame: Dataset with missing values handled.
    """
    threshold = int(0.5 * len(dataFrame))
    dataFrame = dataFrame.dropna(axis=1, thresh=threshold)
    dataFrame.fillna(dataFrame.mean(numeric_only=True), inplace=True)
    return dataFrame

# Method 4: Feature Scaling
def scale_features(dataFrame):
    """
    Scales the 'years_experience' column using StandardScaler.

    Args:
    - dataFrame (DataFrame): The input dataset.

    Returns:
    - DataFrame: Dataset with scaled 'years_experience' feature.
    """
    scaler = StandardScaler()
    dataFrame[['years_experience']] = scaler.fit_transform(dataFrame[['years_experience']])
    return dataFrame, scaler

# Method 5: Prepare Data for Training
def prepare_data(dataFrame):
    """
    Prepares features and target variable for training.

    Args:
    - dataFrame (DataFrame): The input dataset.

    Returns:
    - X (DataFrame): Features (independent variables).
    - y (Series): Target variable (dependent variable).
    """
    X = dataFrame[['years_experience']]  # Independent variable
    y = dataFrame['salary']              # Dependent variable
    return X, y

# Method 6: Split Data into Training and Testing Sets
def split_data(X, y):
    """
    Splits the data into training and testing sets.

    Args:
    - X (DataFrame): Features (independent variables).
    - y (Series): Target variable (dependent variable).

    Returns:
    - X_train (DataFrame): Training features.
    - X_test (DataFrame): Testing features.
    - y_train (Series): Training target variable.
    - y_test (Series): Testing target variable.
    """
    return train_test_split(X, y, test_size=0.2, random_state=42)

# Method 7: Train Linear Regression Model
def train_model(X_train, y_train):
    """
    Trains a Linear Regression model.

    Args:
    - X_train (DataFrame): Training features.
    - y_train (Series): Training target variable.

    Returns:
    - model (LinearRegression): Trained model.
    """
    model = LinearRegression()
    model.fit(X_train, y_train)
    return model

# Method 8: Evaluate Model
def evaluate_model(y_test, y_pred):
    """
    Evaluates the model by calculating R² score and Mean Squared Error (MSE).

    Args:
    - y_test (Series): Actual values from the test set.
    - y_pred (array): Predicted values from the model.

    Returns:
    - r2 (float): R² score.
    - mse (float): Mean Squared Error.
    """
    r2 = r2_score(y_test, y_pred)
    mse = mean_squared_error(y_test, y_pred)
    return r2, mse

# Method 9: Save Model and Scaler
def save_model_and_scaler(model, scaler, model_path, scaler_path):
    """
    Saves the trained model and scaler to disk.

    Args:
    - model (LinearRegression): Trained model.
    - scaler (StandardScaler): Scaler used for feature scaling.
    - model_path (str): Path where the model will be saved.
    - scaler_path (str): Path where the scaler will be saved.
    """
    joblib.dump(scaler, scaler_path)
    joblib.dump(model, model_path)
    print("Model and scaler saved!")

# Main Function
def main():
    # Step 1: Load Data
    dataFrame = load_data("./Source/Salary.csv")

    # Step 2: Remove Duplicates
    dataFrame = remove_duplicates(dataFrame)

    # Step 3: Handle Missing Values
    dataFrame = handle_missing_values(dataFrame)

    # Step 4: Feature Scaling
    dataFrame, scaler = scale_features(dataFrame)

    # Step 5: Prepare Data for Training
    X, y = prepare_data(dataFrame)

    # Step 6: Split Data
    X_train, X_test, y_train, y_test = split_data(X, y)

    # Step 7: Train Model
    model = train_model(X_train, y_train)

    # Step 8: Make Predictions
    y_pred = model.predict(X_test)

    # Step 9: Evaluate Model
    r2, mse = evaluate_model(y_test, y_pred)

    # Print Evaluation Metrics
    print(f"R² Score: {r2:.4f}")
    print(f"Mean Squared Error: {mse:.2f}")

    # Step 10: Model Persistence
    if r2 > 0.95:
        save_model_and_scaler(model, scaler, './Source/salary.pkl', './Source/scaler.pkl')
    else:
        print("Model not saved as R² score is below 95%.")

# Run the main function
if __name__ == "__main__":
    main()
