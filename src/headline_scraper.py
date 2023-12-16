import requests
from bs4 import BeautifulSoup

def scrape_headlines(site, keywords):
    url = site['url']
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        headlines = soup.find_all(attrs=site['headline_attrs'])
        matching_headlines = []
        for headline in headlines:
            headline_text = headline.text.strip()
            for keyword in keywords:
                if keyword.lower() in headline_text.lower():
                    date = headline.find_next(attrs=site['date_attrs'])
                    if date:
                        date_text = date.text.strip()
                    else:
                        date_text = 'Date not found'
                    description = headline.find_next(attrs=site['description_attrs'])
                    if description:
                        description_text = description.text.strip()
                    else:
                        description_text = 'Description not found'
                    matching_headlines.append({'headline':headline_text,
                                            'description':description_text,
                                            'date':date_text,
                                            'url':url,
                                            'business':keywords[0]})
                    break
        return matching_headlines
    else:
        print("Failed to retrieve the webpage. Status code:", response.status_code)

nyt = {'url': 'https://www.nytimes.com/section/business', 'headline_attrs': {'class':'css-1kv6qi e15t083i0'}, 'description_attrs': {'class':'css-1pga48a e15t083i1'}, 'date_attrs': {'data-testid':'todays-date'}}
bbc = {'url': 'https://www.bbc.com/business', 'headline_attrs': {'data-testid': 'card-headline'}, 'description_attrs': {'data-testid': 'card-description'}, 'date_attrs': {'data-testid': 'card-metadata-lastupdated'}}

sites = [nyt, bbc]
companies = [['Netflix', 'NFLX'],
             ['Activision', 'ATVI'],
             ['Apple', 'AAPL', 'iPhone', 'iPad', 'iMac'],
             ['Microsoft', 'MSFT'],
             ['Google', 'GOOG', 'Alphabet', 'GOOGL'],
             ['Facebook', 'FB', 'Instagram', 'WhatsApp'],
             ['Amazon', 'AMZN'],
             ['Tesla', 'TSLA'],
             ['Twitter', 'TWTR'],
             ['Intel', 'INTC'],
             ['AMD', 'Advanced Micro Devices'],
             ['Nvidia', 'NVDA'],
             ['Qualcomm', 'QCOM'],
             ['PayPal', 'PYPL'],
             ['Square', 'SQ'],
             ['Shopify', 'SHOP'],
             ['Etsy', 'ETSY'],
             ]

for site in sites:
    for company in companies:
        headlines = scrape_headlines(site, company)
        print(headlines)