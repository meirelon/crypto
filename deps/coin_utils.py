import pandas as pd
import cbpro

def get_coin_data(ticker="btc", rolling_period=175):
    if not (isinstance(ticker, str)):
        raise TypeError('Input must be a string')

    s = 'https://poloniex.com/public?command=returnChartData&currencyPair=USDT_' + ticker.upper() + '&start=1439020800&end=9999999999&period=14400'
    df = pd.read_json(s)
    df["rolling_min"] = df["close"].rolling(rolling_period).min()
    df["rolling_max"] = df["close"].rolling(rolling_period).max()
    return(df)


def cbpro_auth(k,s,p):
    return cbpro.AuthenticatedClient(k, s, p)
