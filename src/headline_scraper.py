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
                    if site['date_attrs'] is None:
                        date_text = 'Date not found'
                    else:
                        date = headline.find_next(attrs=site['date_attrs'])
                        if date:
                            date_text = date.text.strip()
                        else:
                            date_text = 'Date not found'
                    if site['description_attrs'] is None:
                        description_text = 'Description not found'
                    else:
                        description = headline.find_next(attrs=site['description_attrs'])
                        if description:
                            description_text = description.text.strip()
                        else:
                            description_text = 'Description not found'
                    matching_headlines.append({'headline':headline_text,
                                            'description':description_text,
                                            'date':date_text,
                                            'source':site['name'],
                                            'business':keywords[0]})
                    break
        return matching_headlines
    else:
        print("Failed to retrieve the webpage. Status code:", response.status_code)

nyt = {'name': 'New York Times', 'url': 'https://www.nytimes.com/section/business', 'headline_attrs': {'class':'css-1kv6qi e15t083i0'}, 'description_attrs': {'class':'css-1pga48a e15t083i1'}, 'date_attrs': {'data-testid':'todays-date'}}
bbc = {'name': 'BBC', 'url': 'https://www.bbc.com/business', 'headline_attrs': {'data-testid': 'card-headline'}, 'description_attrs': {'data-testid': 'card-description'}, 'date_attrs': {'data-testid': 'card-metadata-lastupdated'}}
google = {'name': 'Google News', 'url': 'https://news.google.com/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx6TVdZU0FtVnVHZ0pWVXlnQVAB?hl=en-US&gl=US&ceid=US%3Aen', 'headline_attrs': {'class': 'gPFEn'}, 'description_attrs': None, 'date_attrs': {'class': 'hvbAAd'}}
washpo = {'name': 'Washington Post', 'url': 'https://www.washingtonpost.com/business/', 'headline_attrs': {'data-pb-local-content-field':"web_headline"}, 'description_attrs': None, 'date_attrs': None}
# wall street journal
# bloomberg
# financial times
# reuters
# cnbc
# fortune
# business insider
# the economist
# barrons
# marketwatch
# cnn
# fox news
# msnbc
# politico

sites = [nyt, bbc, google, washpo]

company_keywords = [
    ['Apple', 'AAPL', 'iPhone', 'iPad', 'Mac', 'iCloud'],
    ['Microsoft', 'MSFT', 'Windows', 'Office', 'Azure'],
    ['Amazon', 'AMZN', 'AWS', 'Alexa'],
    ['Alphabet', 'GOOGL', 'GOOG', 'Google', 'YouTube'],
    ['Meta', 'META', 'Facebook', 'Instagram'],
    ['Tesla', 'TSLA', 'Elon Musk'],
]


for site in sites:
    for company in company_keywords:
        headlines = scrape_headlines(site, company)
        print(headlines)