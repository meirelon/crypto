import pickle
import time

import pandas as pd
import cbpro

from google.cloud import storage
from tempfile import NamedTemporaryFile

from deps.utils import load_blob, upload_blob

def get_coin_data(ticker="btc", rolling_period=175):
    if not (isinstance(ticker, str)):
        raise TypeError('Input must be a string')

    s = 'https://poloniex.com/public?command=returnChartData&currencyPair=USDT_' + ticker.upper() + '&start=' + str(time.time() - 31556952) + '&end=' + str(time.time()) + '&period=14400'
    df = pd.read_json(s)
    df["rolling_min"] = df["close"].rolling(rolling_period).min()
    df["rolling_max"] = df["close"].rolling(rolling_period).max()
    return(df)


def cbpro_auth(k,s,p):
    return cbpro.AuthenticatedClient(k, s, p)

class CryptoEventTrigger:
    def __init__(self,
                 project,
                 bucket,
                 key,
                 secret,
                 passphrase,
                 ticker,
                 rolling_period,
                 increment):
        self.project=project
        self.bucket=bucket
        self.key=key
        self.secret=secret
        self.passphrase=passphrase
        self.ticker=ticker
        self.rolling_period=rolling_period
        self.increment=increment


    def buy(self, close):
        # auth first
        auth_client = cbpro_auth(self.key,self.secret,self.passphrase)
        account_info = [x for x in auth_client.get_accounts()
                                if x.get("currency").lower() == self.ticker.lower()][0]

        account_amount = (float(account_info.get("available"))*close)

        if account_amount >= self.increment:
            # place order
            auth_client.place_market_order(product_id='{}-USD'.format(self.ticker.upper()),
                                   side='buy',
                                   funds='{}.00'.format(str(self.increment)))

            # record buy and upload blob to storage
            buy_amount = (self.increment)/close
            buy_history.append(buy_amount)

            # temp storage for lambda
            pickle.dump(buy_history, open("/tmp/buy_history.pkl", "wb"))

            # util function to upload buy history to storage
            upload_blob(project_id=self.project,
                            bucket_name=self.bucket,
                            source_file_name="/tmp/buy_history.pkl",
                            destination_blob_name="{t}/{p}_buy_history.pkl".format(t=self.ticker, p=self.passphrase))
            return "Buy"
        else:
            return "Insufficient Funds"

    def sell(self, close, buy_history):
            # auth first
            auth_client = cbpro_auth(self.key,self.secret,self.passphrase)
            # get the sell amount as oldest buy amount
            amount = buy_history.pop(0)
            # calculate sell the dollar value
            sell_amount = amount*close
            # only sell if the amount is greater than your buy increments
            if sell_amount > self.increment:
                auth_client.place_market_order(product_id='{}-USD'.format(self.ticker.upper()),
                                   side='sell',
                                   size=sell_amount)
                return "Sell"
            else:
                buy_history.insert(0,amount)
                return "Sell not bigger then increment"

    def run(self):
            return "something"
