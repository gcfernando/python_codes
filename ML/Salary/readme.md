# Salary Prediction

A machine learning pipeline that trains a Linear Regression model to predict salaries from years of experience, and a separate inference script for making predictions with the saved model.

## Overview

This project has two scripts:

- **`Model Builder/builder.py`** — cleans data, trains the model, evaluates it, and saves it to disk
- **`Prediction/prediction.py`** — loads the saved model and predicts salary from user input

## Scripts

### Model Builder (`builder.py`)

A complete ML pipeline that processes a CSV dataset and produces a trained model.

#### Pipeline Steps

| Step | Action |
|---|---|
| 1 | Load dataset from `Source/Salary.csv` |
| 2 | Remove duplicate rows |
| 3 | Drop columns with >50% missing values; fill remaining nulls with column mean |
| 4 | Scale `years_experience` using `StandardScaler` |
| 5 | Split into 80% train / 20% test sets |
| 6 | Train `LinearRegression` model |
| 7 | Evaluate with R² score and Mean Squared Error |
| 8 | Save model and scaler if R² > 0.95 |

#### Usage

```bash
python "Model Builder/builder.py"
```

**Example output:**
```
R² Score: 0.9762
Mean Squared Error: 31245678.23
Model and scaler saved!
```

If R² ≤ 0.95, the model is not saved and a message is shown instead.

---

### Salary Predictor (`prediction.py`)

Loads the saved model and scaler, accepts user input, and outputs a predicted salary.

#### Usage

```bash
python "Prediction/prediction.py"
```

**Example session:**
```
Enter Years of Experience: 7
Predicted Salary for 7.0 years of experience: $85,234.50
```

---

## Requirements

```
pandas
scikit-learn
joblib
numpy
```

Install dependencies:

```bash
pip install pandas scikit-learn joblib numpy
```

## File Structure

```
Salary/
├── Model Builder/
│   └── builder.py          # Training pipeline
├── Prediction/
│   └── prediction.py       # Inference script
└── Source/
    ├── Salary.csv           # Training dataset (required)
    ├── salary.pkl           # Saved model (generated after training)
    └── scaler.pkl           # Saved scaler (generated after training)
```

## Notes

- Run `builder.py` before `prediction.py` to generate the required `.pkl` files.
- The dataset must contain `years_experience` and `salary` columns.
- The model is only saved when R² exceeds 0.95 to ensure prediction quality.
