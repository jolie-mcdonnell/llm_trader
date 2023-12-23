# THIS SHOULD BE UPDATED TO GET NAMES FROM ALPACA INSTEAD OF YAHOO FINANCE
# THIS WILL ALLOW US TO FILTER OUT STOCK THAT ARE NOT FRACTIONABLE AS WE PROCESS THE LIST OF TICKERS
# see: https://docs.alpaca.markets/docs/working-with-assets

import pandas as pd
import re
import yfinance as yf

# Read stock symbols from local CSV files
NYSE_SYMBOLS = pd.read_csv("data/nyse_stocks.csv")
NASDAQ_SYMBOLS = pd.read_csv("data/nasdaq_stocks.csv")
AMEX_SYMBOLS = pd.read_csv("data/amex_stocks.csv")

TRAILING_CHARS = ",."

COMPANY_SUFFIX_LIST = [
    "agency",
    "gmbh",
    "pa",
    "and",
    "group",
    "pc",
    "assn",
    "hotel",
    "pharmacy",
    "assoc",
    "hotels",
    "plc",
    "associates",
    "inc",
    "pllc",
    "association",
    "incorporated",
    "restaurant",
    "bank",
    "international",
    "sa",
    "bv",
    "intl",
    "sales",
    "co",
    "limited",
    "service",
    "comp",
    "llc",
    "services",
    "company",
    "llp",
    "store",
    "corp",
    "lp",
    "svcs",
    "corporation",
    "ltd",
    "travel",
    "dmd",
    "manufacturing",
    "unlimited",
    "enterprises",
    "mfg",
    "the",
]


def strip_company_suffix(company_name):
    """
    The strip_company_suffix function takes a company name as input and returns the same company name with any suffixes removed.

    :param company_name: The company name to be cleaned up
    """
    # remove punctuation
    for c in TRAILING_CHARS:
        company_name = company_name.replace(c, "")

    # trim quotes and apostrophes
    company_name = company_name.strip("'").strip('"')

    # split company name into words
    words = re.split(r"\s", company_name)

    # remove suffixes from company name
    stripped_name = []
    for word in reversed(words):
        # trim whitespace
        word = word.strip()
        # add word to list if it's not in the suffix list
        if word.lower() in COMPANY_SUFFIX_LIST:
            continue
        else:
            stripped_name.insert(0, word)

    # return cleaned up name as a string
    return " ".join(stripped_name)


def generate_stock_list(symbol):
    """
    The generate_stock_list function takes a stock symbol, fetches the longName from yfinance,
    strips the company suffix (e.g., Inc., Corp.), and returns a tuple of (symbol, longName, [symbol, stripped_name])

    :param symbol: Fetch the stock information from yahoo finance
    """
    try:
        # get stock name from yahoo finance
        stock = yf.Ticker(symbol)
        info = stock.info
        long_name = info.get("longName", "")
        # clean up company name
        stripped_name = strip_company_suffix(long_name)

        print(f"Info fetched successfully for {symbol}")
        # return tuple of (symbol, long_name, [symbol, stripped_name])
        return (
            symbol,
            long_name,
            [symbol, stripped_name],
        )
    except Exception as e:
        print(f"Error fetching info for {symbol}: {e}")
        return None, None, None


# Combine all symbols into one DataFrame
all_symbols = pd.concat([NYSE_SYMBOLS, NASDAQ_SYMBOLS, AMEX_SYMBOLS], ignore_index=True)

# Get company names from yahoo finance
all_symbols[["ticker", "company", "keywords"]] = all_symbols.apply(
    lambda row: generate_stock_list(row.Symbol),
    axis="columns",
    result_type="expand",
)

# Create DataFrame
# df = pd.DataFrame(stocks_info, columns=["ticker", "company"])
df = all_symbols[["ticker", "company", "keywords"]].dropna()

# Save DataFrame to CSV
df.to_csv("data/stocks_info_2.csv", index=False)

print("Script completed. Output saved to stocks_info_2.csv.")
