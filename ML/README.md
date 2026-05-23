# ML

A collection of machine learning projects built with Python.

---

## Projects

### 1. COVID Forecast

**Location:** `COVID Forecast/Console_Code/CovidForecast.py`

A time series forecasting script that predicts the number of daily COVID-19 cases for a country using SARIMAX and auto-ARIMA models.

#### How It Works

1. Downloads daily COVID-19 case data via the `covid_daily` package (if not already cached locally as a CSV)
2. Performs stationarity testing using the **Augmented Dickey-Fuller (ADF)** test
3. Detrends and differences the time series for stationarity
4. Automatically fits the best ARIMA/SARIMA model using `pmdarima.auto_arima`
5. Fits the chosen model using `statsmodels.SARIMAX`
6. Generates a **static forecast** (in-sample) and a **future forecast** for the next N days
7. Displays all charts using `matplotlib`

#### Configuration

Edit these variables at the top of the script:

| Variable | Default | Description |
|---|---|---|
| `country` | `'india'` | Country to forecast (`'india'`, `'brazil'`, etc.) |
| `stepCount` | `50` | Number of future days to forecast |

#### Requirements

```
numpy
pandas
pmdarima
covid_daily
statsmodels
matplotlib
```

```bash
pip install numpy pandas pmdarima covid_daily statsmodels matplotlib
```

#### Usage

```bash
python CovidForecast.py
```

---

### 2. Salary Prediction

**Location:** `Salary/`

A linear regression pipeline that predicts salary based on years of experience.

#### Sub-projects

| File | Purpose |
|---|---|
| `Model Builder/builder.py` | Trains the model and saves it to disk |
| `Prediction/prediction.py` | Loads the saved model and predicts salary from user input |

#### Model Builder Pipeline (`builder.py`)

1. Load data from `Source/Salary.csv`
2. Remove duplicate rows
3. Drop columns with more than 50% missing values; fill remaining nulls with column mean
4. Scale `years_experience` using `StandardScaler`
5. Split into train (80%) and test (20%) sets
6. Train a `LinearRegression` model
7. Evaluate using R² score and Mean Squared Error
8. Save the model and scaler to `Source/salary.pkl` and `Source/scaler.pkl` if R² > 0.95

#### Prediction Inference (`prediction.py`)

1. Load the saved model and scaler from disk
2. Prompt the user for years of experience
3. Scale the input using the saved scaler
4. Predict and display the salary

#### Requirements

```
pandas
scikit-learn
joblib
numpy
```

```bash
pip install pandas scikit-learn joblib numpy
```

#### Usage

**Train the model:**
```bash
python "Salary/Model Builder/builder.py"
```

**Run inference:**
```bash
python "Salary/Prediction/prediction.py"
```

**Example inference session:**
```
Enter Years of Experience: 5
Predicted Salary for 5.0 years of experience: $72,345.67
```

---

## Folder Structure

```
ML/
├── COVID Forecast/
│   └── Console_Code/
│       └── CovidForecast.py       # Time series forecasting script
└── Salary/
    ├── Model Builder/
    │   └── builder.py             # Model training pipeline
    └── Prediction/
        └── prediction.py          # Inference script
```
