import pandas as pd
import re
import yfinance as yf

# Read stock symbols from local CSV files
NYSE_SYMBOLS = pd.read_csv("data/nyse_stocks.csv")
NASDAQ_SYMBOLS = pd.read_csv("data/nasdaq_stocks.csv")
AMEX_SYMBOLS = pd.read_csv("data/amex_stocks.csv")

TRAILING_CHARS = ",.&-"

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
    # Remove trailing characters
    for c in TRAILING_CHARS:
        company_name = company_name.replace(c, "")

    # Remove trailing words from the company suffix list
    words = re.split(r"\s", company_name)
    stripped_name = []

    for word in reversed(words):
        if word.lower() in COMPANY_SUFFIX_LIST:
            continue
        else:
            stripped_name.insert(0, word)

    return " ".join(stripped_name)


def generate_stock_list(symbol, name):
    try:
        stock = yf.Ticker(symbol)
        info = stock.info
        long_name = info.get("longName", "")
        stripped_name = strip_company_suffix(long_name)

        print(f"Info fetched successfully for {symbol}")
        return (
            symbol,
            long_name,
            [symbol, stripped_name],
        )
    except Exception as e:
        print(f"Error fetching info for {symbol}: {e}")
        return None, None, None


# Combine symbols
all_symbols = pd.concat([NYSE_SYMBOLS, NASDAQ_SYMBOLS, AMEX_SYMBOLS], ignore_index=True)
# all_symbols = all_symbols.loc[:10]
# print(all_symbols)

# Fetch stock info from Yahoo Finance
all_symbols[["ticker", "company", "keywords"]] = all_symbols.apply(
    lambda row: generate_stock_list(row.Symbol, row.Name),
    axis="columns",
    result_type="expand",
)

# Create DataFrame
# df = pd.DataFrame(stocks_info, columns=["ticker", "company"])
df = all_symbols[["ticker", "company", "keywords"]].dropna()

# Save DataFrame to CSV
df.to_csv("data/stocks_info_2.csv", index=False)

print("Script completed. Output saved to stocks_info_2.csv.")
