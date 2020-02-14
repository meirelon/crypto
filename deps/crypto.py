import pickle
import time

import pandas as pd
import cbpro

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

    def buy(self, close, buy_history):
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
            buy_history.append(buy_amount)

            # temp storage for lambda
            pickle.dump(buy_history, open("/tmp/buy_history.pkl", "wb"))

            # util function to upload buy history to storage
            upload_blob(project_id=self.project,
                            bucket_name=self.bucket,
                            source_file_name="/tmp/buy_history.pkl",
                            destination_blob_name=f"{self.ticker.lower()}/{self.passphrase}_buy_history.pkl")
            return "Buy"
        else:
            return "Insufficient Funds"

    def sell(self, close, buy_history):
            # auth first
            auth_client = self.cbpro_auth(self.key,self.secret,self.passphrase)
            # get the sell amount as oldest buy amount
            amount = buy_history.pop(0)
            # calculate sell the dollar value
            sell_amount = amount*close
            # only sell if the amount is greater than your buy increments
            if sell_amount > self.increment:
                auth_client.place_market_order(product_id=f'{self.ticker.upper()}-USD',
                                   side='sell',
                                   size=sell_amount)

                # util function to upload buy history to storage
                pickle.dump(buy_history, open("/tmp/buy_history.pkl", "wb"))
                upload_blob(project_id=self.project,
                                bucket_name=self.bucket,
                                source_file_name="/tmp/buy_history.pkl",
                                destination_blob_name=f"{self.ticker.lower()}/{self.passphrase}_buy_history.pkl")
                return "Sell"
            else:
                buy_history.insert(0,amount)
                # util function to upload buy history to storage
                pickle.dump(buy_history, open("/tmp/buy_history.pkl", "wb"))
                upload_blob(project_id=self.project,
                                bucket_name=self.bucket,
                                source_file_name="/tmp/buy_history.pkl",
                                destination_blob_name=f"{self.ticker.lower()}/{self.passphrase}_buy_history.pkl")
                return "Sell not bigger then increment"

    def run(self):
            return "something"
