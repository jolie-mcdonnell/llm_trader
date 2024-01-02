import datetime

import pandas as pd
import requests
from bs4 import BeautifulSoup

# Alpaca has a news API: https://docs.alpaca.markets/docs/news-api which would be faster than scraping,
# but the news is from Benzinga only

google_business = {
    "name": "Google Business News",
    "url": "https://news.google.com/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx6TVdZU0FtVnVHZ0pWVXlnQVAB?hl=en-US&gl=US&ceid=US%3Aen",
    "headline_attrs": {"class": "gPFEn"},
    "description_attrs": None,
    "date_attrs": {"class": "hvbAAd"},
}

google_tech = {
    "name": "Google Technology News",
    "url": "https://news.google.com/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGRqTVhZU0FtVnVHZ0pWVXlnQVAB?hl=en-US&gl=US&ceid=US%3Aen",
    "headline_attrs": {"class": "gPFEn"},
    "description_attrs": None,
    "date_attrs": {"class": "hvbAAd"},
}


def scrape_headlines(
    ticker: str,
    company: str,
    keywords: list,
    site: dict = google_business,
):
    """
    The scrape_headlines function takes in a ticker, company name, list of keywords to search for, and a site dictionary.
    The function then scrapes the website specified by the url key in the site dictionary for headlines that contain any of
    the keywords provided. The function returns a pandas DataFrame containing all matching headlines with their associated
    ticker symbol, company name, and datetime.

    :param ticker: str: The ticker symbol of the company you are looking for
    :param company: str: The name of the company
    :param keywords: list: The keywords to search for in the headlines
    :param site: dict: Information about the website to scrape: name, url, headline_attrs, description_attrs, date_attrs
    :return: A dataframe with the following columns: ticker, company, headline, datetime
    """
    url = site["url"]
    response = requests.get(url)
    if response.status_code == 200:
        # get the html content of the webpage
        soup = BeautifulSoup(response.content, "html.parser")
        # find all headlines on the page
        headlines = soup.find_all(attrs=site["headline_attrs"])
        # loop through headlines and find ones that match the keywords
        matching_headlines = []
        for headline in headlines:
            # get the text of the headline
            headline_text = headline.text.strip()
            # loop through keywords and see if any are in the headline
            for keyword in keywords:
                if len(keyword) < 3:
                    continue
                if keyword.lower() in headline_text.lower():
                    # if the keyword is in the headline, get the date and description
                    if site["date_attrs"] is None:
                        # if no date element attributes are provided, null
                        date = None
                    else:
                        date_element = headline.find_next(attrs=site["date_attrs"])
                        if date_element:
                            date_text = date_element["datetime"]
                            dateUTC = datetime.datetime.strptime(
                                date_text, "%Y-%m-%dT%H:%M:%SZ"
                            )
                            date = dateUTC - datetime.timedelta(hours=5)
                        else:
                            date = None
                    if site["description_attrs"] is None:
                        description_text = "Description not found"
                    else:
                        description = headline.find_next(
                            attrs=site["description_attrs"]
                        )
                        if description:
                            description_text = description.text.strip()
                        else:
                            description_text = "Description not found"
                    # add the headline info to the list of matching headlines
                    matching_headlines.append(
                        {
                            "ticker": ticker,
                            "company": company,
                            "headline": headline_text,
                            # "description": description_text,
                            "datetime": date,
                            # "source": site["name"],
                        }
                    )
                    break
        return pd.DataFrame(matching_headlines)
    else:
        print("Failed to retrieve the webpage. Status code:", response.status_code)


# use this to test
# print(scrape_headlines("AAPL", "Apple", ["AAPL", "Apple"]))

# company_keywords = [
#     ["Apple", "AAPL", "iPhone", "iPad", "Mac", "iCloud"],
#     ["Microsoft", "MSFT", "Windows", "Office", "Azure"],
#     ["Amazon", "AMZN", "AWS", "Alexa"],
#     ["Alphabet", "GOOGL", "GOOG", "Google", "YouTube"],
#     ["Meta", "META", "Facebook", "Instagram"],
#     ["Tesla", "TSLA", "Elon Musk"],
# ]


# for site in sites:
#     for company in company_keywords:
#         headlines = scrape_headlines(site, company)
#         print(headlines)
