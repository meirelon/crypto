import time

import pandas as pd

def get_coin_data(ticker="btc", rolling_period=175):
    if not (isinstance(ticker, str)):
        raise TypeError('Input must be a string')

    time_end = time.time()
    time_start = time_end - 31556952

    s = f'https://poloniex.com/public?command=returnChartData&currencyPair=USDT_{ticker.upper()}&start={time_start}&end={time_end}&period=14400'
    df = pd.read_json(s)
    df["rolling_min"] = df["close"].rolling(rolling_period).min()
    df["rolling_max"] = df["close"].rolling(rolling_period).max()
    return [df, df.iloc[-1,:]["close"], df.iloc[-1,:]["rolling_min"], df.iloc[-1,:]["rolling_max"]]
