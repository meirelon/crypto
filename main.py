import os
import pickle

import pandas as pd

from deps.coin_utils import get_coin_data, CryptoEventTrigger
from deps.utils import load_blob, upload_blob

def crypto(request):
    if request.method == "POST":
        r = request.get_json()
        project = r["project_id"]
        bucket = r["bucket"]
        key = r["cbpro_key"]
        secret = r["cbpro_secret"]
        passphrase = r["cbpro_passphrase"]
        ticker = r["ticker"]
        rolling_period = r["rolling_period"]
        increment = r["increment"]
        increment_float = float(increment)
    else:
        return "missing parameters"

    try:
        # Read in buy history from storage
        buy_history = load_blob(project_id=project,
                                bucket_name=bucket,
                                destination_path=ticker,
                                filename="{}_buy_history.pkl".format(passphrase))
    except:
        # if the buy history for this account does not exist
        # create a new list and upload to storage
        buy_history = []
        pickle.dump(buy_history, open("/tmp/buy_history.pkl", "wb"))
        upload_blob(project_id=project,
                        bucket_name=bucket,
                        source_file_name="/tmp/buy_history.pkl",
                        destination_blob_name="{t}/{p}_buy_history.pkl".format(t=ticker, p=passphrase))


    crypto_event = CryptoEventTrigger(project=project,
                                    bucket=bucket,
                                    key=key,
                                    secret=secret,
                                    passphrase=passphrase,
                                    ticker=ticker,
                                    rolling_period=int(rolling_period),
                                    increment=float(increment))





    df = get_coin_data(ticker, int(rolling_period))
    close = df.iloc[-1,:]["close"]
    rolling_min = df.iloc[-1,:]["rolling_min"]
    rolling_max = df.iloc[-1,:]["rolling_max"]

    # buy event
    if close <= rolling_min:
        buy_event = crypto_event.buy(close=close)
        return buy_event

    # sell event
    if close >= rolling_max and len(buy_history)>0:
        sell_event = crypto_event.sell(close=close, buy_history=buy_history)
        return sell_event
