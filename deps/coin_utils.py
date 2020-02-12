import pandas as pd
import cbpro

def get_coin_data(ticker="btc", rolling_period=175):
    if not (isinstance(ticker, str)):
        raise TypeError('Input must be a string')
    s = 'https://poloniex.com/public?command=returnChartData&currencyPair=USDT_' + ticker.upper() + '&start=1439020800&end=9999999999&period=14400'
    try:
        df = pd.read_json(s)
        df.rename(index=str, columns = {list(df)[1]:'date'}, inplace=True)
        df["rolling_min"] = df["btc_close"].rolling(rolling_period).min()
        df["rolling_max"] = df["btc_close"].rolling(rolling_period).max()
        return(df)
    except:
        print('%s failed' % ticker.upper())
        pass


def cbpro_auth(k,s,p):
    return cbpro.AuthenticatedClient(k, s, p)
