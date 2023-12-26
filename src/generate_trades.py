from datetime import datetime

import pandas as pd
from pytz import timezone

from headline_scraper import scrape_headlines
from llm_call import generate_stock_recommendation

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

S3_BUCKET = "llm-trader"

TRADES_MORNING_FILE = f"s3://{S3_BUCKET}/data/trades_morning.csv"
TRADES_AFTERNOON_FILE = f"s3://{S3_BUCKET}data/trades_afternoon.csv"

# List of dataframes containing headlines for each stock
RESULT_LIST = []


def process_row(
    row: pd.Series,
):
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
        (df["datetime"].dt.date == datetime.now().date())
        & (df["datetime"].dt.time >= TRADING_CATEGORIES[trade_category]["start"])
        & (df["datetime"].dt.time <= TRADING_CATEGORIES[trade_category]["end"])
    ]
    return df


def row_to_model(row: pd.Series):
    """
    The row_to_model function takes in a row from the dataframe and feeds it into the model.

    :param row: pd.Series: Pass the row of data from the dataframe to the function
    """
    # Get headline
    headline = row["headline"]

    # Get company name
    company_name = row["company"]

    # Get term
    term = "short"

    # Get recommendation
    return generate_stock_recommendation(headline, company_name, term)


def pre_market(df: pd.DataFrame):
    """
    The pre_market function takes in a dataframe of sentiments and generates trades for each stock.
    It then writes the trades to the trades_morning.csv and trades_afternoon.csv files.

    :param df: pd.DataFrame: Pass the dataframe of sentiments to the function
    """
    # If news is positive, buy then sell (long)
    # If news is negative, sell then buy (short)
    # Write first trades to trades_morning.csv
    # Write second trades to trades_afternoon.csv
    morning_trades = pd.concat(
        [
            pd.DataFrame(
                {
                    "ticker": df[df["recommendation"] > 0]["ticker"],
                    "side": "buy",
                }
            ),
            pd.DataFrame(
                {
                    "ticker": df[df["recommendation"] < 0]["ticker"],
                    "side": "sell",
                }
            ),
        ]
    )
    morning_trades.to_csv(TRADES_MORNING_FILE, mode="a", header=False, index=False)


def during_market(df: pd.DataFrame):
    """
    The during_market function takes in a dataframe of sentiments and generates trades for each stock.
    It then writes the trades to the trades_afternoon.csv file.

    :param df: pd.DataFrame: Pass the dataframe of sentiments to the function
    """
    # If news is positive, buy then sell (long)
    # If news is negative, sell then buy (short)
    # Write first trades to trades_afternoon.csv
    afternoon_trades = pd.concat(
        [
            pd.DataFrame(
                {
                    "ticker": df[df["recommendation"] > 0]["ticker"],
                    "side": "buy",
                }
            ),
            pd.DataFrame(
                {
                    "ticker": df[df["recommendation"] < 0]["ticker"],
                    "side": "sell",
                }
            ),
        ]
    )
    afternoon_trades.to_csv(TRADES_AFTERNOON_FILE, mode="a", header=False, index=False)


def after_hours(df: pd.DataFrame):
    """
    The after_hours function takes in a dataframe of sentiments and generates trades for each stock.
    It then writes the trades to the trades_morning.csv file.

    :param df: pd.DataFrame: Pass the dataframe of sentiments to the function
    """
    # If news is positive, buy then sell (long)
    # If news is negative, sell then buy (short)
    # Write first trades to trades_morning.csv
    morning_trades = pd.concat(
        [
            pd.DataFrame(
                {
                    "ticker": df[df["recommendation"] > 0]["ticker"],
                    "side": "buy",
                }
            ),
            pd.DataFrame(
                {
                    "ticker": df[df["recommendation"] < 0]["ticker"],
                    "side": "sell",
                }
            ),
        ]
    )
    morning_trades.to_csv(TRADES_MORNING_FILE, mode="a", header=False, index=False)


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

    # Feed all timely headlines into model
    result_df["recommendation"] = result_df.apply(row_to_model, axis=1)

    result_df.to_csv("recommendation_test.csv")  # for testing

    rec_df = result_df[["ticker", "recommendation"]]

    # Get average sentiment in model output, group by ticker
    avg_df = rec_df.groupby("ticker").mean()
    # reshape to [ticker, recommendation]
    avg_df = avg_df.reset_index()

    avg_df.to_csv("sentiment_test.csv")  # for testing

    # Generate trades for each stock
    if trade_category == 1:
        pre_market(avg_df)
    elif trade_category == 2:
        during_market(avg_df)
    elif trade_category == 3:
        after_hours(avg_df)


generate_trades("data/stocks_info_test.csv")

# trade_category = 1
# move yesterday's _afternoon trades to today's afternoon trades
# transfer_afternoon_trades()
# get headlines from midnight to 9:30-x AM EST - starting with 8AM
# feed headlines into model, get average sentiment
# insert trades for today at open (trades_morning.csv) and today at close (trades_afternoon.csv)
# if positive, buy then sell (long)
# if negative, sell then buy (short)

# trade_category = 2
# get headlines from 9:30 AM EST to 4:00-x PM EST - starting with 2:30PM
# feed headlines into model, get average sentiment
# insert trades for today at close (trades_afternoon.csv) and  at close (trades__afternoon.csv)
# if positive, buy then sell (long)
# if negative, sell then buy (short)

# trade_category = 3
# get headlines from 4:00 PM EST to midnight - starting with 10:30PM
# feed headlines into model, get average sentiment
# insert trades for  at open (trades_morning.csv) and  at close (trades__afternoon.csv)
# if positive, buy then sell (long)
# if negative, sell then buy (short)
