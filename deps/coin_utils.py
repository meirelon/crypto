import pandas as pd

def get_coin_data(ticker, rolling_period=175):
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



def buy_event(df, buy_history=[]):
    latest_record = len(df)-1
    if df.iloc[latest_record,:]["close"] <= df.iloc[latest_record,:]["rolling_min"]:
        buy = 100/df.iloc[latest_record,:]["close"]
        buy_history.append(buy)
        return [True, buy_history]



def sell_event(df, buy_history=[]):
    latest_record
    if df.iloc[latest_record,:]["close"] >= df.iloc[latest_record,:]["rolling_max"] and len(buy_history)>0:
        btc_amount = buy_history.pop(0)
        sell = btc_amount*df.iloc[latest_record,:]["close"]
        if sell < 100:
            buy_history.insert(0,btc_amount)


def cbpro_auth(k,s,p):
    return cbpro.AuthenticatedClient(k, s, p)
