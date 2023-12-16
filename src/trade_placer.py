import alpaca_trade_api as tradeapi
import os


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
            return "Invalid trade strategy. Please use 'buy' or 'sell'."

        # Submit the order
        api.submit_order(
            symbol=ticker,
            qty=num_shares,
            side=trade_strategy,
            type="market",
        )

        return f"Successfully submitted a {trade_strategy} limit order for {ticker}."

    except Exception as e:
        return f"Error executing the trade: {str(e)}"


if __name__ == "__main__":
    # Example usage
    ticker = "BYON"
    trade_strategy = "sell"
    dollar_amount = 100

    result = execute_trade(ticker, trade_strategy, dollar_amount)
    print(result)
