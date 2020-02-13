import os
import pickle

import pandas as pd
import cbpro

from google.cloud import storage
from tempfile import NamedTemporaryFile


from deps.utils import upload_blob, load_blob
from deps.coin_utils import get_coin_data, cbpro_auth

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
        return "still testing... first"

    try:
        # Read in buy history from storage
        buy_history = load_blob(project_id=project,
                                bucket_name=bucket,
                                destination_path=ticker,
                                filename="{}_buy_history.pkl".format(passphrase))
    except:
        buy_history = []
        pickle.dump(buy_history, open("/tmp/buy_history.pkl", "wb"))
        upload_blob(project_id=project,
                        bucket_name=bucket,
                        source_file_name="/tmp/buy_history.pkl",
                        destination_blob_name="{t}/{p}_buy_history.pkl".format(t=ticker, p=passphrase))

    df = get_coin_data(ticker, int(rolling_period))
    latest_record = len(df)-1
    close = df.iloc[latest_record,:]["close"]
    rolling_min = df.iloc[latest_record,:]["rolling_min"]
    rolling_max = df.iloc[latest_record,:]["rolling_max"]

    # buy event
    if close <= rolling_min:
        # auth first
        auth_client = cbpro_auth(key,secret,passphrase)
        account_info = [x for x in auth_client.get_accounts()
                                if x.get("currency").lower() == ticker.lower()][0]

        if (float(account_info.get("available"))*close)>=increment_float:
            # place order
            auth_client.place_market_order(product_id='{}-USD'.format(ticker.upper()),
                                   side='buy',
                                   funds='{}.00'.format(increment))

            # record buy and upload blob to storage
            buy = increment_float/close
            buy_history.append(buy)

            # temp storage for lambda
            pickle.dump(buy_history, open("/tmp/buy_history.pkl", "wb"))

            # util function to upload buy history to storage
            upload_blob(project_id=project,
                            bucket_name=bucket,
                            source_file_name="/tmp/buy_history.pkl",
                            destination_blob_name="{t}/{p}_buy_history.pkl".format(t=ticker, p=passphrase))
            return "Buy"

    # sell event
    if close >= rolling_max and len(buy_history)>0:
        # auth first
        auth_client = cbpro_auth(key,secret,passphrase)
        # get the sell amount as oldest buy amount
        amount = buy_history.pop(0)
        # calculate sell the dollar value
        sell = amount*df.iloc[latest_record,:]["close"]
        # only sell if the amount is greater than your buy increments
        if sell > increment_float:
            auth_client.place_market_order(product_id='{}-USD'.format(ticker.upper()),
                               side='sell',
                               size=sell)
        else:
            buy_history.insert(0,amount)
        return "Sell"
    return "No Buy Or Sell"
