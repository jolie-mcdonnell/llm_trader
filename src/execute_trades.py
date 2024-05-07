import os
from datetime import datetime

import alpaca_trade_api as tradeapi
import pandas as pd
import pandas_market_calendars as mcal
from pytz import timezone


TRADES_MORNING_FILE = "data/trades_morning.csv"
TRADES_AFTERNOON_FILE = "data/trades_afternoon.csv"
TRADES_TEST_FILE = "data/trades_morning_test.csv"
BUYING_POWER = 1000.0

# Set Alpaca API key and secret
API_KEY = os.getenv("ALPACA_API_KEY")
API_SECRET = os.getenv("ALPACA_SECRET_KEY")

# Create an Alpaca API connection
API = tradeapi.REST(
    API_KEY,
    API_SECRET,
    base_url="https://paper-api.alpaca.markets",
    api_version="v2",
)


# Orders on Alpaca: https://docs.alpaca.markets/docs/orders-at-alpaca
# Short selling rules: https://docs.alpaca.markets/docs/margin-and-short-selling
# Fractional trading: https://docs.alpaca.markets/docs/fractional-trading


def is_weekend_or_holiday():
    """
    The is_weekend_or_holiday function checks if today is a weekend or holiday.

    :return: A boolean value - true if today is weekend or holiday
    """

    # Calendar:'XNYS', or New York Stock Exchange
    calendar_name = "XNYS"

    # Get the market calendar
    calendar = mcal.get_calendar(calendar_name)

    # Get today's date
    tz = timezone("America/New_York")
    today = datetime.now(tz).date()

    # Check if today is a weekend or a holiday
    is_weekend = today.weekday() >= 5  # Saturday (5) or Sunday (6)
    # Check if today is a holiday
    valid_days = calendar.valid_days(start_date=today, end_date=today)
    is_holiday = len(valid_days) == 0
    return is_weekend or is_holiday


def execute_trade(ticker: str, side: str, num_shares: float):
    """
    The execute_trade function takes in a ticker symbol, trade side (buy or sell).
    It then checks the available buying power to ensure there's enough for the trade. If so, it executes
    the order using Alpaca's API.

    :param ticker: Specify the stock ticker symbol
    :param side: Determine whether to buy or sell the stock
    """
    print(ticker, side, num_shares)

    # Execute the trade
    try:
        # Submit the order
        API.submit_order(
            symbol=ticker,
            qty=num_shares,
            side=side,
            type="market",
        )

        print(f"Successfully submitted a {side} limit order for {ticker}.")

    except Exception as e:
        print(f"Error executing the trade: {str(e)}")


def get_last_trade_price(ticker: str):
    """
    The get_last_trade_price function takes a ticker symbol as input and returns the last trade price for that stock.

    :param ticker: str: Specify the ticker of the stock to get
    :return: The last trade price for a given ticker
    """

    try:
        # Get the last trade information
        last_trade = API.get_latest_trade(ticker)
        API.get_asset(ticker).fractionable

        # Extract the last trade price
        last_trade_price = last_trade.price

        return last_trade_price

    except Exception as e:
        print(f"Error getting last trade price for {ticker}: {str(e)}")
        return None


def fractionable(ticker: str):
    """
    The fractionable function takes a ticker symbol as an argument and returns whether or not the asset is fractionable.
        This function is used to determine if we can buy/sell partial shares of a stock.

    :param ticker: Specify the ticker of the asset
    :return: A boolean value, true or false
    """

    # print(ticker, API.get_asset(ticker).fractionable)
    try:
        return API.get_asset(ticker).fractionable
    except:
        return None


def get_num_shares(trades_df: pd.DataFrame):
    """
    The get_num_shares function takes in a trades_df and returns the same dataframe with an additional column, num_shares.
    The num_shares column is calculated by first splitting the trades into buy and sell orders. The buying power per share is then calculated as BUYING_POWER / number of shares to be bought (len(trades)).
    For each sell order, we check if it's last trade price is less than or equal to our buying power per share. If so, we add that stock to our list of stocks that can be sold for cash. We then update our total buying power by subtracting the sum

    :param trades_df:Pass in a dataframe of trades
    :return: A dataframe with the number of shares to buy or sell for each ticker
    """
    global BUYING_POWER

    buying_power_per_share = BUYING_POWER / len(trades_df)

    trades_df["fractionable"] = trades_df.ticker.apply(fractionable)
    trades_df.dropna(axis=1, how="all")

    # split into buy and sell df
    trades_df_non_fractionable = trades_df[
        (trades_df.side == "sell") | (trades_df.fractionable == False)
    ]
    trades_df_fractionable = trades_df[
        (trades_df.side == "buy") & (trades_df.fractionable)
    ]

    # get cost of a share and subset sell df to shares we can afford

    trades_df_non_fractionable["last_trade_price"] = (
        trades_df_non_fractionable.ticker.apply(get_last_trade_price)
    )
    trades_df_non_fractionable = trades_df_non_fractionable[
        trades_df_non_fractionable.last_trade_price <= buying_power_per_share
    ]

    # update buying power for fractionable orders
    BUYING_POWER = BUYING_POWER - trades_df_non_fractionable.last_trade_price.sum()
    buying_power_per_share = BUYING_POWER / (len(trades_df_fractionable))
    print(
        f"Buying power after sell orders: {BUYING_POWER:.2f}, ${buying_power_per_share:.2f} per share"
    )

    # drop last trade price column
    trades_df_non_fractionable = trades_df_non_fractionable.drop(
        ["last_trade_price"], axis=1
    )

    # set num_shares for all remaining non fractional orders to 1
    trades_df_non_fractionable["num_shares"] = 1

    # compute num shares for remaining orders
    trades_df_fractionable["last_trade_price"] = trades_df_fractionable.ticker.apply(
        get_last_trade_price
    )
    trades_df_fractionable["num_shares"] = trades_df_fractionable.apply(
        lambda x: buying_power_per_share / x.last_trade_price, axis=1
    )
    trades_df_fractionable = trades_df_fractionable.drop(["last_trade_price"], axis=1)

    return pd.concat(
        [trades_df_non_fractionable, trades_df_fractionable], ignore_index=True
    )


def execute_trades_handler(trades_file: str):
    """
    The execute_trades_handler function takes in a trades_file, which is a csv file containing the following columns:
        ticker - The stock symbol of the security to be traded.
        side - The trading side to be used for this trade.  Currently supported strategies are 'buy' and 'sell'.
    :param trades_file: Read the trades from the file and execute them
    """

    trades_df = pd.read_csv(trades_file).drop_duplicates(
        subset="ticker", keep="last"
    )  # drop duplicate recommendations keeping latest

    trades_df = get_num_shares(trades_df)

    # execute trades
    trades_df.apply(lambda x: execute_trade(x.ticker, x.side, x.num_shares), axis=1)

    # clear out trades df
    pd.DataFrame(
        columns=[
            "ticker",
            "side",
        ]
    ).to_csv(trades_file, index=False)


def execute_trades():
    """
    The execute_trades function is responsible for executing trades based on the
    trades file that is passed in. The function will read in the trades file, and then
    execute each trade by calling the execute_trade function. After all of the trades have been executed,
    the positions will be updated to reflect any changes made during execution.
    """

    tz = timezone("America/New_York")
    current_time = datetime.now(tz).time()

    print(current_time.strftime("%H:%M:%S"))

    if is_weekend_or_holiday():
        raise Exception("Cannot trade on weekend or holiday")

    # if current execution time is in window #1, read in morning trades file
    if (current_time >= datetime.strptime("09:10:00", "%H:%M:%S").time()) & (
        current_time <= datetime.strptime("09:40:00", "%H:%M:%S").time()
    ):
        print("time window 1")
        execute_trades_handler(TRADES_MORNING_FILE)

    # if current execution time is in window #2, read in afternoon trades file
    elif (current_time >= datetime.strptime("15:40:00", "%H:%M:%S").time()) & (
        current_time <= datetime.strptime("16:00:00", "%H:%M:%S").time()
    ):
        print("time window 2")

        # Close all open positions
        API.close_all_positions()

        # Execute afternoon trades
        execute_trades_handler(TRADES_AFTERNOON_FILE)

    else:
        raise Exception("Execution time not in morning or afternoon window")


if __name__ == "__main__":
    # try:
    #     execute_trades()
    # except Exception as e:
    #     print(f"Error executing trades: {str(e)}")
    execute_trades()
