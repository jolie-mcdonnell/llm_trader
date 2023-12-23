import os
from datetime import datetime

import alpaca_trade_api as tradeapi
import pandas as pd
from pytz import timezone

TRADES_MORNING_FILE = "data/trades_morning.csv"
TRADES_AFTERNOON_FILE = "data/trades_afternoon.csv"
TRADES_TEST_FILE = "data/trades_morning_test.csv"

# Orders on Alpaca: https://docs.alpaca.markets/docs/orders-at-alpaca
# Short selling rules: https://docs.alpaca.markets/docs/margin-and-short-selling
# Fractional trading: https://docs.alpaca.markets/docs/fractional-trading

# TODO: Count number of positions in the current window and spread the buying power evenly across them
# When we implement short selling, we'll need to be sure we keep enough buying power to cover the shorts


def execute_trade(ticker, side, dollar_amount):
    """
    The execute_trade function takes in a ticker symbol, trade side (buy or sell), and dollar amount.
    It then checks the available buying power to ensure there's enough for the trade. If so, it executes
    the order using Alpaca's API.

    :param ticker: Specify the stock ticker symbol
    :param side: Determine whether to buy or sell the stock
    :param dollar_amount: Determine how much money to trade
    """

    # Set your Alpaca API key and secret
    api_key = os.getenv("ALPACA_API_KEY")
    api_secret = os.getenv("ALPACA_SECRET_KEY")

    # Create an Alpaca API connection
    api = tradeapi.REST(
        api_key,
        api_secret,
        base_url="https://paper-api.alpaca.markets",
        api_version="v2",
    )

    # Get account information to check available balance
    account_info = api.get_account()
    buying_power = float(account_info.buying_power)

    # Validate if there's enough buying power for the trade
    if side == "buy" and dollar_amount > buying_power:
        return "Not enough buying power to execute the buy trade."

    # Execute the trade
    try:
        # Get the last trade information
        last_trade = api.get_latest_trade(ticker)

        # Calculate limit price with adjustments
        if side == "buy":
            num_shares = dollar_amount / float(last_trade.price)
        elif side == "sell":
            num_shares = round(dollar_amount / float(last_trade.price), 0)

        else:
            raise Exception("Invalid trade side. Please use 'buy' or 'sell'.")

        # Submit the order
        api.submit_order(
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
        amount - The number of shares to buy or sell.

    :param trades_file: Read the trades from the file and execute them
    """

    trades_df = pd.read_csv(trades_file)
    trades_df.apply(lambda x: execute_trade(x.ticker, x.side, x.amount), axis=1)
    pd.DataFrame().to_csv(trades_file, index=False)


def execute_trades():
    """
    The execute_trades function is the main function that will be called by the scheduler.
    It reads in a trades file, and executes all of the trades contained within it.
    The function takes no arguments, but does require that you have set up your environment variables correctly.
    """

    tz = timezone("EST")
    current_time = datetime.now(tz).time()

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
        execute_trades_handler(TRADES_AFTERNOON_FILE)

    else:
        print("time window test")
        execute_trades_handler(TRADES_TEST_FILE)
        print("Exception will be raised")
        # raise Exception("Execution time not in morning or afternoon window")


# TODO: delete this
if __name__ == "__main__":
    execute_trades()
