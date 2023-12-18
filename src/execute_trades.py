import os
from datetime import datetime

import alpaca_trade_api as tradeapi
import pandas as pd
from pytz import timezone

TRADES_MORNING_FILE = "data/trades_morning.csv"
TRADES_AFTERNOON_FILE = "data/trades_afternoon.csv"
TRADES_TEST_FILE = "data/trades_morning_test.csv"


def execute_trade(ticker, trade_strategy, dollar_amount):
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
    if trade_strategy == "buy" and dollar_amount > buying_power:
        return "Not enough buying power to execute the buy trade."

    # Execute the trade
    try:
        # Get the last trade information
        last_trade = api.get_latest_trade(ticker)

        # Calculate limit price with adjustments
        if trade_strategy == "buy":
            num_shares = dollar_amount / float(last_trade.price)
        elif trade_strategy == "sell":
            num_shares = round(dollar_amount / float(last_trade.price), 0)

        else:
            raise Exception("Invalid trade strategy. Please use 'buy' or 'sell'.")

        # Submit the order
        api.submit_order(
            symbol=ticker,
            qty=num_shares,
            side=trade_strategy,
            type="market",
        )

        print(f"Successfully submitted a {trade_strategy} limit order for {ticker}.")

    except Exception as e:
        print(f"Error executing the trade: {str(e)}")


def execute_trades():
    tz = timezone("EST")
    current_time = datetime.now(tz).time()

    trades_df = pd.read_csv(TRADES_TEST_FILE)

    # if current execution time is in window #1, read in morning trades file
    if (current_time >= datetime.strptime("05:50:00", "%H:%M:%S").time()) & (
        current_time <= datetime.strptime("06:00:00", "%H:%M:%S").time()
    ):
        print("time window 1")
        trades_df = pd.read_csv(TRADES_MORNING_FILE)

    # if current execution time is in window #2, read in afternoon trades file
    elif (current_time >= datetime.strptime("15:50:00", "%H:%M:%S").time()) & (
        current_time <= datetime.strptime("16:00:00", "%H:%M:%S").time()
    ):
        print("time window 2")
        trades_df = pd.read_csv(TRADES_AFTERNOON_FILE)

    else:
        print("Exception will be raised")
        # raise Exception("Execution time not in morning or afternoon window")

    trades_df.apply(lambda x: execute_trade(x.ticker, x.strategy, x.amount), axis=1)


# TODO: delete this
if __name__ == "__main__":
    execute_trades()
