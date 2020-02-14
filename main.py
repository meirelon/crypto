import os
import pickle

import pandas as pd

from deps.coin_utils import get_coin_data
from deps.storage import load_blob, upload_blob, get_buy_history
from deps.crypto import CryptoEventTrigger

def crypto(request):
    if request.method == "POST":
        r = request.get_json()
        project = r["project_id"]
        bucket = r["bucket"]
        key = r["cbpro_key"]
        secret = r["cbpro_secret"]
        passphrase = r["cbpro_passphrase"]
        ticker = r["ticker"]
        rolling_period = int(r["rolling_period"])
        increment = r["increment"]
        increment_float = float(increment)
    else:
        return abort(405)
        return "missing parameters"




    crypto_event = CryptoEventTrigger(project=project,
                                    bucket=bucket,
                                    key=key,
                                    secret=secret,
                                    passphrase=passphrase,
                                    ticker=ticker,
                                    rolling_period=rolling_period,
                                    increment=float(increment))

    buy_history = get_buy_history(project, bucket, ticker, passphrase)



    df = get_coin_data(ticker, rolling_period)
    close = df.iloc[-1,:]["close"]
    rolling_min = df.iloc[-1,:]["rolling_min"]
    rolling_max = df.iloc[-1,:]["rolling_max"]

    # buy event
    if close <= rolling_min:
        buy_event = crypto_event.buy(close=close, buy_history=buy_history)
        return buy_event

    # sell event
    if close >= rolling_max and len(buy_history) > 0:
        sell_event = crypto_event.sell(close=close, buy_history=buy_history)
        return sell_event

    return "No Buy or Sell"
