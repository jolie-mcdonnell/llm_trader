import requests
from bs4 import BeautifulSoup

def scrape_headlines(site, keywords):
    url = site['url']
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    headlines = []
    
    for headline in soup.find_all(site['headline_div']):
        for keyword in keywords:
            if keyword.lower() in headline.text.lower():
                date = headline.find_next(site['date_div']).text
                headlines.append({'headline': headline.text, 'date': date})
    
    return headlines


def main():
    site = {'url': 'https://www.bbc.com/news', 'headline_div': 'h2', 'date_div': 'span'}
    keywords = ['Google', 'GOOG', 'Alphabet', 'GOOGL'];
    headlines = scrape_headlines(site, keywords)
    print(headlines)

if __name__ == '__main__':
    main()