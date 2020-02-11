import os
import pickle

import pandas as pd
import numpy as np

import cbpro


from deps.utils import upload_blob, load_blob
import deps.coin_utils as coin_utils
def crypto_event():
    project = os.environ["PROJECT_ID"]

    key = os.environ["CBPRO_KEY"]
    secret = os.environ["CBPRO_SECRET"]
    passphrase = os.environ["CBPRO_PASSPHRASE"]

    bucket = os.environ["GCS_BUCKET"]
    ticker = os.environ["TICKER"]


    auth_client = coin_utils.cbpro_auth()

    if auth_client.get_accounts()[2].get("available")>100:
        buy_history = load_blob(project_id=project,
                                bucket_name=bucket,
                                destination_path=ticker,
                                filename="buy_history.pkl")

        df = coin_utils.get_coin_data(ticker)

        coin_utils.buy_event(df, buy_history)

        auth_client.place_market_order(product_id='BTC-USD',
                               side='buy',
                               funds='100.00')

    return True
