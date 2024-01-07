import os
from datetime import datetime

import alpaca_trade_api as tradeapi
import pandas as pd
import pandas_market_calendars as mcal
from pytz import timezone


S3_BUCKET = "llm-trader"

TRADES_MORNING_FILE = f"s3://{S3_BUCKET}/data/trades_morning.csv"
TRADES_AFTERNOON_FILE = f"s3://{S3_BUCKET}data/trades_afternoon.csv"
TRADES_TEST_FILE = f"s3://{S3_BUCKET}/data/trades_morning_test.csv"

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


# TODO: Count number of positions in the current window and spread the buying power evenly across them
# When we implement short selling, we'll need to be sure we keep enough buying power to cover the shorts


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
    tz = timezone("EST")
    today = datetime.now(tz).date()

    # Check if today is a weekend or a holiday
    is_weekend = today.weekday() >= 5  # Saturday (5) or Sunday (6)
    # Check if today is a holiday
    valid_days = calendar.valid_days(start_date=today, end_date=today)
    is_holiday = len(valid_days) == 0
    return is_weekend or is_holiday


def execute_trade(ticker: str, side):
    """
    The execute_trade function takes in a ticker symbol, trade side (buy or sell).
    It then checks the available buying power to ensure there's enough for the trade. If so, it executes
    the order using Alpaca's API.

    :param ticker: Specify the stock ticker symbol
    :param side: Determine whether to buy or sell the stock
    """

    # Get account information to check available balance
    # account_info = API.get_account()
    # buying_power = float(account_info.buying_power)

    # # Validate if there's enough buying power for the trade
    # if side == "buy" and dollar_amount > buying_power:
    #     return "Not enough buying power to execute the buy trade."

    # Execute the trade
    try:
        # # Get the last trade information
        # last_trade = API.get_latest_trade(ticker)

        # # Calculate limit price with adjustments
        # if side == "buy":
        #     num_shares = dollar_amount / float(last_trade.price)
        # elif side == "sell":
        #     num_shares = round(dollar_amount / float(last_trade.price), 0)
        # else:
        #     raise Exception("Invalid trade side. Please use 'buy' or 'sell'.")

        # Buy/sell 1 at a time for simplicity
        num_shares = 1

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


def execute_trades_handler(trades_file):
    """
    The execute_trades_handler function takes in a trades_file, which is a csv file containing the following columns:
        ticker - The stock symbol of the security to be traded.
        side - The trading side to be used for this trade.  Currently supported strategies are 'buy' and 'sell'.
    :param trades_file: Read the trades from the file and execute them
    """

    trades_df = pd.read_csv(trades_file).drop_duplicates(
        subset="ticker", keep="last"
    )  # drop duplicate recommendations keeping latest

    # execute trades
    trades_df.apply(lambda x: execute_trade(x.ticker, x.side), axis=1)

    # clear out trades df
    pd.DataFrame(
        columns=[
            "ticker",
            "strategy",
        ]
    ).to_csv("out.csv", index=False)


def execute_trades():
    """
    The execute_trades function is responsible for executing trades based on the
    trades file that is passed in. The function will read in the trades file, and then
    execute each trade by calling the execute_trade function. After all of the trades have been executed,
    the positions will be updated to reflect any changes made during execution.
    """

    tz = timezone("EST")
    current_time = datetime.now(tz).time()

    if is_weekend_or_holiday():
        raise Exception("Cannot trade on weekend or holiday")

    # if current execution time is in window #1, read in morning trades file
    if (current_time >= datetime.strptime("05:50:00", "%H:%M:%S").time()) & (
        current_time <= datetime.strptime("06:00:00", "%H:%M:%S").time()
    ):
        print("time window 1")
        execute_trades_handler(TRADES_MORNING_FILE)

    # if current execution time is in window #2, read in afternoon trades file
    elif (current_time >= datetime.strptime("15:50:00", "%H:%M:%S").time()) & (
        current_time <= datetime.strptime("16:00:00", "%H:%M:%S").time()
    ):
        print("time window 2")

        # Close all open positions
        API.close_all_positions()

        # Execute afternoon trades
        execute_trades_handler(TRADES_AFTERNOON_FILE)

    else:
        print("time window test")
        execute_trades_handler(TRADES_TEST_FILE)
        print("Exception will be raised")
        # raise Exception("Execution time not in morning or afternoon window")


# # TODO: delete this
# if __name__ == "__main__":
#     execute_trades()
