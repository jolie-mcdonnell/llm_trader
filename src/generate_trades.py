from datetime import datetime
import time

import pandas as pd
from pytz import timezone

from headline_scraper import scrape_all_headlines
from llm_call import generate_stock_recommendation

# 1 is pre-market, 2 is during market hours, 3 is after hours
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


# List of dfs containing headlines for each stock
RESULT_LIST = []


def search_headlines(
    row: pd.Series,
    headlines: pd.DataFrame,
):
    """
    The search_headlines function takes in a row from the dataframe and finds matching headlines for that company.
    It then returns a dictionary with all of the information about that company's news.

    :param row: pd.Series: Pass the row of data from the dataframe to the function
    """
    matching_headlines = []
    for _, headline in headlines.iterrows():
        for keyword in row["keywords"].strip("[]").replace("'", "").split(", "):
            if len(keyword) < 3:
                continue
            if keyword.lower() in headline["headline"].lower():
                matching_headlines.append(
                    {
                        "ticker": row["ticker"],
                        "company": row["company"],
                        "headline": headline["headline"],
                        "datetime": headline["datetime"],
                    }
                )
                break
    RESULT_LIST.append(pd.DataFrame(matching_headlines))


def get_trading_category():
    """
    The get_trading_category function gets the current trading category based on the current time.
    """
    # Get current time
    tz = timezone("America/New_York")
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
    rec = generate_stock_recommendation(headline, company_name, term)
    return rec


def pre_market(df: pd.DataFrame):
    """
    The pre_market function takes in a dataframe of sentiments and generates trades for each stock.
    It then writes the trades to the trades_morning.csv file.

    :param df: pd.DataFrame: Pass the dataframe of sentiments to the function
    """
    # If news is positive, long the stock
    # If news is negative, short the stock
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
    # with open(TRADES_MORNING_FILE, "a") as f:
    #     f.write("\n")


def during_market(df: pd.DataFrame):
    """
    The during_market function takes in a dataframe of sentiments and generates trades for each stock.
    It then writes the trades to the trades_afternoon.csv file.

    :param df: pd.DataFrame: Pass the dataframe of sentiments to the function
    """
    # If news is positive, long the stock
    # If news is negative, short the stock
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
    # with open(TRADES_MORNING_FILE, "a") as f:
    #     f.write("\n")


def after_hours(df: pd.DataFrame):
    """
    The after_hours function takes in a dataframe of sentiments and generates trades for each stock.
    It then writes the trades to the trades_morning.csv file.

    :param df: pd.DataFrame: Pass the dataframe of sentiments to the function
    """
    # If news is positive, long the stock
    # If news is negative, short the stock
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
    # with open(TRADES_MORNING_FILE, "a") as f:
    #     f.write("\n")


def generate_trades(stocks_file: str):
    # Load list of stocks
    stocks = pd.read_csv(stocks_file)

    # Get all headlines
    print("\U0001F30E scraping headlines:", end=" ", flush=True)
    scrape_start = time.time()
    all_headlines = scrape_all_headlines()
    print("%.1f seconds" % (time.time() - scrape_start))

    # all_headlines.to_csv("temp/all_headlines.csv", index=False) # for testing

    # Get trading category
    trade_category = get_trading_category()

    # Filter headlines based on trade category
    filter_start = time.time()
    print("\U0001F552 filtering headlines by time:", end=" ", flush=True)
    timely_headlines = headline_filter(all_headlines, trade_category)
    print("%.1f seconds" % (time.time() - filter_start))

    # timely_headlines.to_csv("temp/timely_headlines.csv", index=False) # for testing

    # For each stock, search through all headlines
    print("\U0001F50D searching headlines for stocks:", end=" ", flush=True)
    search_start = time.time()
    stocks.apply(search_headlines, axis=1, args=(timely_headlines,))
    print("%.1f seconds" % (time.time() - search_start))

    # Concatenate all dataframes into one
    result_df = pd.concat(RESULT_LIST, ignore_index=True)

    # result_df.to_csv("temp/result_df.csv", index=False) # for testing

    # Feed all timely headlines into model
    print("\U0001F916 feeding headlines into model:", end=" ", flush=True)
    model_start = time.time()

    result_df["recommendation"] = result_df.apply(row_to_model, axis=1)
    rec_df = result_df[["ticker", "recommendation"]]
    # rec_df.to_csv("temp/rec_df.csv", index=False) # for testing
    # Get average sentiment in model output, group by ticker
    avg_df = rec_df.groupby("ticker").mean()
    # reshape to [ticker, recommendation]
    avg_df = avg_df.reset_index()
    print("%.1f seconds" % (time.time() - model_start))

    # avg_df.to_csv("temp/avg_df.csv", index=False) # for testing

    # Write trades
    print("\U0001f4dd writing trades:", end=" ", flush=True)
    write_start = time.time()
    if trade_category == 1:
        pre_market(avg_df)
    elif trade_category == 2:
        during_market(avg_df)
    elif trade_category == 3:
        after_hours(avg_df)
    print("%.1f seconds" % (time.time() - write_start))


if __name__ == "__main__":
    print("welcome to generate_trades!")
    start_time = time.time()
    # print(start_time.strftime("%H:%M:%S"))
    # generate_trades("data/stocks_info_test.csv")  # for testing
    generate_trades("data/stocks_info_3.csv")
    print(f"total time: {round(time.time() - start_time, 1)} seconds")
