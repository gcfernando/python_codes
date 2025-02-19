# Developer ::> Gehan Fernando
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
import joblib

# Step 1: Load Data
dataFrame = pd.read_csv("./Source/Salary.csv")

# Step 2: Check for Duplicates
duplicate_count = dataFrame.duplicated().sum()
if duplicate_count > 0:
    dataFrame.drop_duplicates(inplace=True)
    dataFrame.reset_index(drop=True, inplace=True)

# Step 3: Handle Missing Values
threshold = int(0.5 * len(dataFrame))
dataFrame = dataFrame.dropna(axis=1, thresh=threshold)
dataFrame.fillna(dataFrame.mean(numeric_only=True), inplace=True)

# Step 4: Feature Scaling (Standardize features) - only years_experience
scaler = StandardScaler()
dataFrame[['years_experience']] = scaler.fit_transform(dataFrame[['years_experience']])  # Correct column name
joblib.dump(scaler, './Source/scaler.pkl')  # Save the scaler

# Step 5: Prepare Data for Training
X = dataFrame[['years_experience']]
y = dataFrame['salary']

# Step 6: Split Data into Training and Testing Sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Step 7: Initialize and Train the Model
model = LinearRegression()
model.fit(X_train, y_train)

# Step 8: Make Predictions on the Test Set
y_pred = model.predict(X_test)

# Step 9: Evaluate Model Performance
r2 = r2_score(y_test, y_pred)
mse = mean_squared_error(y_test, y_pred)

# Print r2 value
print(f"R² Score: {r2:.4f}")

# Step 10: Save the Model if Performance is Satisfactory
if r2 > 0.95:
    joblib.dump(model, './Source/salary.pkl')
    print("Model saved!")
else:
    print("Model not saved as R² score is below 95%.")
