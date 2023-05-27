'''
https://www.bounteous.com/insights/2020/09/15/forecasting-time-series-model-using-python-part-one/
https://www.bounteous.com/insights/2020/09/15/forecasting-time-series-model-using-python-part-two/

https://github.com/Bounteous-Inc/Time-Series-Prediction/blob/master/Time%20Series%20Prediction%20Temp.ipynb
'''

# Import libraries
import warnings
import numpy as np
import pandas as pd
import pmdarima as pm
import covid_daily as cd
import statsmodels.api as sm
import matplotlib.pyplot as plt
import matplotlib.ticker as tick
import matplotlib.dates as mdates

from os import path
from statsmodels.tsa.stattools import adfuller

# Ignore harmless warnings
warnings.filterwarnings('ignore')

plt.style.use('fast')

# Initialize variables
stepCount = 50
frequency = 'D'
country = 'india'  # india, brazil
fileName = f'{country}_corvid19.csv'
indexColumn = 'Date'
newColumn = 'Daily Cases'
title = f'{country.capitalize()} COVID-19 {newColumn.lower()} forcasting for next {stepCount} days'

if not path.exists(fileName):
    # Download file
    dataset = cd.data(country=country, chart='graph-cases-daily', as_json=False)
    # Rename column
    dataset.rename(columns={'Novel Coronavirus Daily Cases': newColumn}, inplace=True)
    # Fill Null values with 0
    dataset[newColumn].fillna(0, inplace=True)
    # Change values to decimal
    dataset[newColumn].astype(float)
    # Save to file
    dataset.to_csv(fileName)

    print(f'{fileName} file downloaded.')

# Load data
dataset = pd.read_csv(fileName, parse_dates=True, index_col=indexColumn)
dataset = dataset.asfreq('D')

y = dataset[newColumn]


def printLog(value):
    if value != "":
        print(value)

    print('\r\n')


def showPlot(ax, title=''):
    ax.set_xlabel(indexColumn)
    ax.set_ylabel(newColumn)
    ax.autoscale()
    ax.grid(color='b', linestyle='--')

    if title != '':
        plt.title(title)

    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%b'))

    plt.gcf().autofmt_xdate()

    plt.legend()
    plt.show()


def ADF_test(timeseries, dataDesc):
    print(' > Is the {} stationary ?'.format(dataDesc))
    dftest = adfuller(timeseries, autolag='AIC')
    print('Test statistic = {:.3f}'.format(dftest[0]))
    print('P-value = {:.3f}'.format(dftest[1]))
    print('Critical values :')

    for k, v in dftest[4].items():
        print('\t{}: {} - The data is {} stationary with {}% confidence'.format(k,
              v, 'not' if v < dftest[0] else '', 100-int(k[:-1])))

    printLog('')


def test_stationarity(timeseries, title):
    # Determing rolling statistics
    rolmean = pd.Series(timeseries).rolling(window=12).mean()
    rolstd = pd.Series(timeseries).rolling(window=12).std()

    fig, ax = plt.subplots()
    ax.plot(timeseries, label=title)
    ax.plot(rolmean, label='rolling mean')
    ax.plot(rolstd, label='rolling std (x10)')
    ax.legend()
    ax.grid()

    plt.show()


def staticForecast(model):
    start = pd.to_datetime(y.index[len(y.index) - 120])
    pred = model.get_prediction(start=start, dynamic=False, full_results=True)
    pred_ci = pred.conf_int()

    ax = y[str(start.year):].plot(label=newColumn)
    pred.predicted_mean.plot(ax=ax, label='Static Forecast', alpha=.7)

    ax.fill_between(pred_ci.index,
                    pred_ci.iloc[:, 0],
                    pred_ci.iloc[:, 1], color='k', alpha=.2)

    showPlot(ax)


def forecast(model, predict_steps, y):
    pred_uc = model.get_forecast(steps=predict_steps)
    pred_ci = pred_uc.conf_int()

    pm = pred_uc.predicted_mean.reset_index()
    pm.columns = [indexColumn, 'Predicted Mean']
    pci = pred_ci.reset_index()
    pci.columns = [indexColumn, 'Lower Bound', 'Upper Bound']

    final_table = pm.join(pci.set_index(indexColumn), on=indexColumn)

    print(final_table)

    ax = y.plot(label=newColumn)
    pred_uc.predicted_mean.plot(ax=ax, label='Forecast')
    ax.fill_between(pred_ci.index,
                    pred_ci.iloc[:, 0],
                    pred_ci.iloc[:, 1], color='k', alpha=.25)
    ax.get_yaxis().set_major_formatter(tick.FuncFormatter(lambda x, p: format(int(x), ',')))
    showPlot(ax, title)


# Detrending
y_detrend = (y - y.rolling(window=12).mean())/y.rolling(window=12).std()
# Detrending + Differencing
y_12lag_detrend = y_detrend - y_detrend.shift(12)

y_12lag_detrend.replace([np.inf, -np.inf], np.nan, inplace=True)
y_12lag_detrend.dropna(inplace=True)

# Check for Stationarity
ADF_test(y_12lag_detrend, '12 lag differenced de-trended data')
test_stationarity(y_12lag_detrend, '12 lag differenced de-trended data')

autoModel = pm.auto_arima(
    y=y, start_p=2, d=None, start_q=2, max_p=50, max_d=50, max_q=50, start_P=2, D=None, start_Q=2, max_P=50, max_D=50,
    max_Q=50, max_order=None, m=12, seasonal=True, information_criterion='aic', alpha=0.05, test='adf', stepwise=True,
    n_jobs=-1, maxiter=100, suppress_warnings=True, error_action='ignore', trace=True, n_fits=100,
    out_of_sample_size=80, random=True, random_state=80)

printLog(autoModel.summary())

# Fitting an ARIMA Time Series Model
mod = sm.tsa.statespace.SARIMAX(y, freq=frequency,
                                order=(autoModel.order),
                                seasonal_order=autoModel.seasonal_order,
                                enforce_stationarity=False,
                                enforce_invertibility=False)

model = mod.fit(method='powell', maxiter=100, optim_score='approx', optim_complex_step=True, disp=-1)

printLog(model.summary())

staticForecast(model)
forecast(model, stepCount, y)