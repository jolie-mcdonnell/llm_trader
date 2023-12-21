from llm_call import generate_stock_recommendation
import os
from datetime import datetime

import pandas as pd
from pytz import timezone

import pandas as pd


TRADES_MORNING_FILE = "data/trades_morning.csv"
TRADES_AFTERNOON_FILE = "data/trades_afternoon.csv"
TRADES_TOMORROW_ATERNOON_FILE = "data/trades_tomorrow_afternoon.csv"


def transfer_afternoon_trades():
    # Read data from tomorrow afternoon trades csv
    df_tomorrow_afternoon = pd.read_csv(TRADES_TOMORROW_ATERNOON_FILE)

    # Overwrite this afternoon's files with df_tomorrow_afternoon
    df_tomorrow_afternoon.to_csv(TRADES_AFTERNOON_FILE, index=False)

    # Delete the rows from trades_tomorrow_afternoon.csv
    pd.DataFrame().to_csv(TRADES_TOMORROW_ATERNOON_FILE, index=False)


def generate_trade():
    return


def generate_trades():
    # get trading category

    tz = timezone("EST")
    current_time = datetime.now(tz).time()

    if (current_time >= datetime.strptime("05:45:00", "%H:%M:%S").time()) & (
        current_time <= datetime.strptime("06:00:00", "%H:%M:%S").time()
    ):
        trade_category = 1
        transfer_afternoon_trades()

    elif (current_time >= datetime.strptime("15:45:00", "%H:%M:%S").time()) & (
        current_time <= datetime.strptime("16:00:00", "%H:%M:%S").time()
    ):
        trade_category = 2

    # elif (current_time >= datetime.strptime("21:45:00", "%H:%M:%S").time()) & (
    elif (current_time >= datetime.strptime("18:00:00", "%H:%M:%S").time()) & (
        current_time <= datetime.strptime("00:00:00", "%H:%M:%S").time()
    ):
        trade_category = 3
