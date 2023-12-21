import nltk
import pandas as pd
import yfinance as yf
from nltk import pos_tag, word_tokenize

nltk.download("punkt")
nltk.download("averaged_perceptron_tagger")

# Read stock symbols from local CSV files
nyse_symbols = pd.read_csv("data/nyse_stocks.csv")
nasdaq_symbols = pd.read_csv("data/nasdaq_stocks.csv")
amex_symbols = pd.read_csv("data/amex_stocks.csv")

# Combine symbols
all_symbols = pd.concat([nyse_symbols, nasdaq_symbols, amex_symbols], ignore_index=True)

# Define unwanted keywords
unwanted_keywords = [
    "Common",
    "Stock",
    "Corp",
    "Company",
    "Inc",
    "Corporation",
    "Inc.",
    "Acquisition",
    "Holdings",
]

# Fetch stock info from Yahoo Finance
stocks_info = []
for symbol in all_symbols["Symbol"]:
    try:
        print(f"Fetching info for {symbol}...")
        stock = yf.Ticker(symbol)
        info = stock.info
        long_name = info.get("longName", "")

        # Tokenize and extract keywords from the long name
        tokens = word_tokenize(long_name)
        keywords = [
            word
            for word, tag in pos_tag(tokens)
            if tag.startswith("NN") or tag.startswith("JJ")
        ]

        # Remove unwanted keywords
        filtered_keywords = [kw for kw in keywords if kw not in unwanted_keywords]

        stocks_info.append(
            {
                "Ticker": info.get("symbol", ""),
                "Company Name": " ".join(filtered_keywords),
            }
        )
        print(f"Info fetched successfully for {symbol}")
    except Exception as e:
        print(f"Error fetching info for {symbol}: {e}")

# Create DataFrame
df = pd.DataFrame(stocks_info, columns=["ticker", "company"])

# Save DataFrame to CSV
df.to_csv("data/stocks_info.csv", index=False)

print("Script completed. Output saved to stocks_info.csv.")
