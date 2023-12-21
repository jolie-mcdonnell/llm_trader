from llm_call import generate_stock_recommendation
from headline_scraper import scrape_headlines_sites
import os
from datetime import datetime

import pandas as pd
from pytz import timezone

import pandas as pd


TRADES_MORNING_FILE = "data/trades_morning.csv"
TRADES_AFTERNOON_FILE = "data/trades_afternoon.csv"
TRADES_TOMORROW_ATERNOON_FILE = "data/trades_tomorrow_afternoon.csv"


def transfer_afternoon_trades():
    """
    The transfer_afternoon_trades function is used to transfer the trades that are made yesterday afternoon
    to be transferred to today's afternoon trades. This function is called at 4:00 PM EST every day.
    """
    # Read data from tomorrow afternoon trades csv
    df_tomorrow_afternoon = pd.read_csv(TRADES_TOMORROW_ATERNOON_FILE)

    # Overwrite this afternoon's files with df_tomorrow_afternoon
    df_tomorrow_afternoon.to_csv(TRADES_AFTERNOON_FILE, index=False)

    # Delete the rows from trades_tomorrow_afternoon.csv
    pd.DataFrame().to_csv(TRADES_TOMORROW_ATERNOON_FILE, index=False)


def generate_trade():
    return


RESULT_LIST = []


def process_row(row: pd.Series):
    """
    The process_row function takes in a row from the dataframe and scrapes the headlines for that company.
    It then returns a dictionary with all of the information about that company's news.

    :param row: pd.Series: Pass the row of data from the dataframe to the function
    """

    result = scrape_headlines_sites(row["ticker"], row["company"], row["keywords"])
    RESULT_LIST.append(result)


def generate_trades(stocks_file: str):
    # load in list of stocks to extract info for
    df = pd.read_csv(stocks_file)

    df.apply(process_row, axis=1)

    result_df = pd.concat(RESULT_LIST, ignore_index=True)
    result_df.to_csv("headline_test.csv")

    # get trading category

    tz = timezone("EST")
    current_time = datetime.now(tz).time()

    # time window 1
    if (current_time >= datetime.strptime("05:45:00", "%H:%M:%S").time()) & (
        current_time <= datetime.strptime("06:00:00", "%H:%M:%S").time()
    ):
        trade_category = 1
        transfer_afternoon_trades()

    # time window 2
    elif (current_time >= datetime.strptime("15:45:00", "%H:%M:%S").time()) & (
        current_time <= datetime.strptime("16:00:00", "%H:%M:%S").time()
    ):
        trade_category = 2

    # time window 3
    elif (current_time >= datetime.strptime("21:45:00", "%H:%M:%S").time()) & (
        # elif (current_time >= datetime.strptime("18:00:00", "%H:%M:%S").time()) & ( # for testing
        current_time
        <= datetime.strptime("00:00:00", "%H:%M:%S").time()
    ):
        trade_category = 3


generate_trades("data/stocks_info_test.csv")
