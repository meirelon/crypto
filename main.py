import os
import pickle

import pandas as pd

from deps.coin_utils import get_coin_data
from deps.crypto import CryptoEventTrigger, EventOutcome

def crypto(request):
    try:
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
    except Exception as e:
        return e




    crypto_event = CryptoEventTrigger(project=project,
                                    bucket=bucket,
                                    key=key,
                                    secret=secret,
                                    passphrase=passphrase,
                                    ticker=ticker,
                                    rolling_period=rolling_period,
                                    increment=float(increment))


    df, close, rolling_min, rolling_max = get_coin_data(ticker,
                                                        rolling_period)

    # buy event
    if close <= rolling_min:
        buy_event = crypto_event.run(transaction_type=EventOutcome.BUY,
                                     close=close)
        return buy_event

    # sell event
    if close >= rolling_max:
        sell_event = crypto_event.run(transaction_type=EventOutcome.SELL,
                                      close=close)
        return sell_event

    return "No Buy or Sell"
