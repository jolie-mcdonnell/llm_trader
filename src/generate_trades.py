from llm_call import generate_stock_recommendation
from headline_scraper import scrape_headlines
import os
from datetime import datetime

import pandas as pd
from pytz import timezone

import pandas as pd

# 1 is pre-market, 2 is during market hours, 3 is after-hours
TRADING_CATEGORIES = {
    1: {
        "start": datetime.strptime("00:00:00", "%H:%M:%S").time(),
        "end": datetime.strptime("09:30:00", "%H:%M:%S").time(),
    },
    2: {
        "start": datetime.strptime("09:30:00", "%H:%M:%S").time(),
        "end": datetime.strptime("16:00:00", "%H:%M:%S").time(),
    },
    3: {
        "start": datetime.strptime("16:00:00", "%H:%M:%S").time(),
        "end": datetime.strptime("23:59:59", "%H:%M:%S").time(),
    },
}

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


# List of dataframes containing headlines for each stock
RESULT_LIST = []


def process_row(row: pd.Series):
    """
    The process_row function takes in a row from the dataframe and scrapes the headlines for that company.
    It then returns a dictionary with all of the information about that company's news.

    :param row: pd.Series: Pass the row of data from the dataframe to the function
    """
    result = scrape_headlines(
        row["ticker"],
        row["company"],
        row["keywords"].strip("[]").replace("'", "").split(", "),
    )
    RESULT_LIST.append(result)


def get_trading_category():
    """
    The get_trading_category function gets the current trading category based on the current time.
    """
    # Get current time
    tz = timezone("EST")
    current_time = datetime.now(tz).time()

    # THIS IS A WEIRD WAY TO DO THIS
    # time window 1 (pre-market)
    if (current_time >= TRADING_CATEGORIES[1]["start"]) & (
        current_time <= TRADING_CATEGORIES[1]["end"]
    ):
        trade_category = 1

    # time window 2 (during market hours)
    elif (current_time >= TRADING_CATEGORIES[2]["start"]) & (
        current_time <= TRADING_CATEGORIES[2]["end"]
    ):
        trade_category = 2

    # time window 3 (after-hours)
    elif (current_time >= TRADING_CATEGORIES[3]["start"]) & (
        current_time <= TRADING_CATEGORIES[3]["end"]
    ):
        trade_category = 3

    return trade_category


def headline_filter(df: pd.DataFrame, trade_category: int):
    """
    The headline_filter function takes in a dataframe of headlines and filters them based on the trade category.
    It then returns a dataframe with the filtered headlines.

    :param df: pd.DataFrame: Pass the dataframe of headlines to the function
    :param trade_category: int: Pass the trade category to the function
    """
    # filter headlines based on trade category
    df = df[
        (df["date"].dt.date == datetime.now().date())
        & (df["date"].dt.time >= TRADING_CATEGORIES[trade_category]["start"])
        & (df["date"].dt.time <= TRADING_CATEGORIES[trade_category]["end"])
    ]
    return df


def generate_trades(stocks_file: str):
    # Load list of stocks
    df = pd.read_csv(stocks_file)

    # Get all headlines for each stock
    df.apply(process_row, axis=1)

    # Concatenate all dataframes into one
    result_df = pd.concat(RESULT_LIST, ignore_index=True)
    # result_df.to_csv("headline_test.csv") # for testing

    # Get trading category
    trade_category = get_trading_category()

    # Filter headlines based on trade category
    result_df = headline_filter(result_df, trade_category)

    result_df.to_csv("headline_test.csv")  # for testing

    # TODO: Feed all windowed headlines into model

    # TODO: Get average sentiment in model output, group by ticker

    # TODO: Generate trades for each stock


generate_trades("data/stocks_info_test.csv")

# trade_category = 1
# move yesterday's tomorrow_afternoon trades to today's afternoon trades
# transfer_afternoon_trades()
# get headlines from midnight to 9:30-x AM EST
# feed headlines into model, get average sentiment
# insert trades for today at open (trades_morning.csv) and today at close (trades_afternoon.csv)
# if positive, buy then sell (long)
# if negative, sell then buy (short)

# trade_category = 2
# get headlines from 9:30 AM EST to 4:00-x PM EST
# feed headlines into model, get average sentiment
# insert trades for today at close (trades_afternoon.csv) and tomorrow at close (trades_tomorrow_afternoon.csv)
# if positive, buy then sell (long)
# if negative, sell then buy (short)

# trade_category = 3
# get headlines from 4:00 PM EST to midnight
# feed headlines into model, get average sentiment
# insert trades for tomorrow at open (trades_morning.csv) and tomorrow at close (trades_tomorrow_afternoon.csv)
# if positive, buy then sell (long)
# if negative, sell then buy (short)
