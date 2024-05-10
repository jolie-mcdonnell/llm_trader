import os
import finnhub
import time
import pandas as pd

import datetime as dt

FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")

# Initialize the Finnhub client with your API key
finnhub_client = finnhub.Client(api_key=FINNHUB_API_KEY)
today = dt.datetime.today().date()
COUNTER = 0


def get_headlines(ticker):
    global COUNTER
    try:
        # Fetch news headlines for the ticker from Finnhub API
        news = finnhub_client.company_news(symbol=ticker, _from=today, to=today)
        # Extract headlines from the response
        headlines = [(article["headline"], article["datetime"]) for article in news]
        COUNTER += 1
        print(COUNTER)
        return headlines
    except:
        time.sleep(5)
        get_headlines(ticker)


if __name__ == "__main__":
    start_time = time.time()

    stocks = pd.read_csv("data/stocks_info_3.csv")

    stocks = stocks[["ticker", "company"]]
    stocks["result"] = stocks["ticker"].apply(get_headlines)
    stocks = stocks.explode("result")
    stocks[["headline", "datetime"]] = stocks["result"].apply(pd.Series)
    stocks.drop("result", axis=1, inplace=True)
    stocks = stocks.dropna()

    stocks.to_csv("data/finnhub_headlines.csv", mode="a", header=False, index=False)

    end_time = time.time()

    elapsed_time = end_time - start_time

    print("Elapsed time:", elapsed_time, "seconds")
