import os
import pickle

import pandas as pd
import cbpro

from google.cloud import storage
from tempfile import NamedTemporaryFile


from deps.utils import upload_blob, load_blob
import deps.coin_utils as coin_utils
def crypto_event(request):
    project = os.environ["PROJECT_ID"]
    bucket = os.environ["GCS_BUCKET"]

    key = os.environ["CBPRO_KEY"]
    secret = os.environ["CBPRO_SECRET"]
    passphrase = os.environ["CBPRO_PASSPHRASE"]

    ticker = os.environ["TICKER"]

    rolling_period = os.environ["ROLLING_PERIOD"]
    increment = os.environ["INCREMENT"]
    increment_int = int(increment)

    # Read in buy history from storage
    buy_history = load_blob(project_id=project,
                            bucket_name=bucket,
                            destination_path=ticker,
                            filename="buy_history.pkl")

    df = coin_utils.get_coin_data(ticker, int(rolling_period))
    latest_record = len(df)-1

    # buy event
    if df.iloc[latest_record,:]["close"] <= df.iloc[latest_record,:]["rolling_min"]:
        # auth first
        auth_client = coin_utils.cbpro_auth(key,secret,passphrase)
        if auth_client.get_accounts()[2].get("available")>=increment_int:
            # place order
            auth_client.place_market_order(product_id='{}-USD'.format(ticker.upper()),
                                   side='buy',
                                   funds='{}.00'.format(increment))

            # record buy and upload blob to storage
            buy = int(increment)/df.iloc[latest_record,:]["close"]
            buy_history.append(buy)

            # temp storage for lambda
            pickle.dump(buy_history, open("tmp/buy_history.pkl", "wb"))

            # util function to upload buy history to storage
            upload_blob(project_id=project,
                            bucket_name=bucket,
                            source_file_name="buy_history.pkl",
                            destination_blob_name="{}/buy_history.pkl".format(ticker))

    # sell event
    if df.iloc[latest_record,:]["close"] >= df.iloc[latest_record,:]["rolling_max"] and len(buy_history)>0:
        # auth first
        auth_client = coin_utils.cbpro_auth(key,secret,passphrase)
        # get the sell amount as oldest buy amount
        btc_amount = buy_history.pop(0)
        # calculate sell the dollar value
        sell = btc_amount*df.iloc[latest_record,:]["close"]
        # only sell if the amount is greater than your buy increments
        if sell > increment_int:
            auth_client.place_market_order(product_id='BTC-USD',
                               side='sell',
                               size=sell)
        else:
            buy_history.insert(0,btc_amount)
    return True
