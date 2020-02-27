import pickle
import time
from enum import Enum

import pandas as pd
import cbpro

from deps.storage import load_blob, upload_blob, get_buy_history, dump_and_upload

class EventOutcome(Enum):
    BUY = "buy"
    SELL = "sell"

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


    def cbpro_auth(k,s,p):
        return cbpro.AuthenticatedClient(k, s, p)

    def buy(self, close):
        # auth first
        auth_client = self.cbpro_auth(self.key,self.secret,self.passphrase)
        account_info = [x for x in auth_client.get_accounts()
                                if x.get("currency").lower() == self.ticker.lower()][0]

        account_amount = (float(account_info.get("available"))*close)

        if account_amount >= self.increment:
            # place order
            auth_client.place_market_order(product_id=f'{self.ticker.upper()}-USD',
                                   side='buy',
                                   funds=f'{self.increment}.00')

            # record buy and upload blob to storage
            buy_amount = (self.increment)/close
            buy_history = get_buy_history(self.project, self.bucket, self.ticker, self.passphrase)
            buy_history.append(buy_amount)

            dump_and_upload(obj=buy_history,
                            project=self.project,
                            bucket=self.bucket,
                            ticker=self.ticker,
                            passphrase=self.passphrase)
            return EventOutcome.BUY
        else:
            return "Insufficient Funds"

    def sell(self, close):
            # only sell if the amount is greater than your buy increments
            buy_history = get_buy_history(self.project, self.bucket, self.ticker, self.passphrase)
            if len(buy_history) > 0:
                # get the sell amount as oldest buy amount
                amount = buy_history.pop(0)
                # calculate sell the dollar value
                sell_amount = amount*close
                if sell_amount > self.increment:
                    # auth first
                    auth_client = self.cbpro_auth(self.key,self.secret,self.passphrase)
                    # then make the sell
                    auth_client.place_market_order(product_id=f'{self.ticker.upper()}-USD',
                                       side='sell',
                                       size=sell_amount)

                    # util function to upload buy history to storage
                    dump_and_upload(obj=buy_history,
                                    project=self.project,
                                    bucket=self.bucket,
                                    ticker=self.ticker,
                                    passphrase=self.passphrase)
                    return EventOutcome.SELL
                else:
                    buy_history.insert(0,amount)
                    # util function to upload buy history to storage
                    dump_and_upload(obj=buy_history,
                                    project=self.project,
                                    bucket=self.bucket,
                                    ticker=self.ticker,
                                    passphrase=self.passphrase)
                    return "Sell not bigger then increment"
            else:
                return "No buy history"

    def run(self, transaction_type, close):
        if transaction_type.lower() == "buy":
            self.buy(close=close)
        if transaction_type.lower() == "sell":
            self.sell(close=close)
            return "something"
