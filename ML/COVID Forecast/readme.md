# COVID Forecast

A time series forecasting script that predicts daily COVID-19 cases for a country using SARIMAX and auto-ARIMA models.

## Overview

This script downloads daily COVID-19 case data, performs stationarity analysis, automatically selects the best ARIMA/SARIMA model, fits it, and generates both an in-sample static forecast and a future forecast for the next N days. All results are visualized with `matplotlib`.

## Features

- Automatically downloads COVID-19 daily case data if not cached locally
- Augmented Dickey-Fuller (ADF) stationarity test with detailed output
- Rolling mean and standard deviation visualization for stationarity inspection
- Automatic ARIMA/SARIMA parameter selection via `pmdarima.auto_arima`
- SARIMAX model fitting using `statsmodels`
- Static (in-sample) forecast for the last 120 days
- Future forecast for the next N days with confidence intervals
- All plots displayed with gridlines, auto-scaled axes, and monthly date formatting

## Requirements

```
numpy
pandas
pmdarima
covid_daily
statsmodels
matplotlib
```

Install dependencies:

```bash
pip install numpy pandas pmdarima covid_daily statsmodels matplotlib
```

## Configuration

Edit the variables at the top of `CovidForecast.py`:

| Variable | Default | Description |
|---|---|---|
| `country` | `'india'` | Country to forecast (`'india'`, `'brazil'`, etc.) |
| `stepCount` | `50` | Number of future days to forecast |
| `frequency` | `'D'` | Time series frequency (`'D'` = daily) |

## Usage

```bash
python CovidForecast.py
```

On first run, a CSV file (e.g., `india_corvid19.csv`) is downloaded and saved in the working directory. Subsequent runs load from this cached file.

### Output

1. ADF test results printed to console
2. Rolling statistics chart (stationarity check)
3. Static forecast chart (last 120 days vs. in-sample prediction)
4. Future forecast chart with confidence interval shading and a table of predicted values

## How It Works

1. Data is loaded and resampled to daily frequency
2. A 12-period rolling detrend and differencing step is applied to achieve stationarity
3. `auto_arima` searches for the best ARIMA order using AIC and an ADF test for differencing
4. The SARIMAX model is fit with Powell optimization
5. Static and dynamic forecasts are generated and plotted

## File Structure

```
COVID Forecast/
└── Console_Code/
    └── CovidForecast.py    # Main script
```
