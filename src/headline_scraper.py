import requests
from bs4 import BeautifulSoup

def scrape_headlines(site, keywords):
    url = site['url']
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    headlines = soup.find_all('h3')
    matching_headlines = []
    for headline in headlines:
        for keyword in keywords:
            if keyword.lower() in headline.text.lower():
                # date = headline.find_next('span', attrs={'data-testid': "todays-date"}).text
                matching_headlines.append({'headline':headline.text, 'url':url, 'business':keywords[0]})
                break
    return matching_headlines

nyt_business = {'url': 'https://www.nytimes.com/section/business', 'headline_tag': 'h3'}
bbc = {'url': 'https://www.bbc.com/news', 'headline_tag': 'h2'}

print(scrape_headlines(nyt_business, ['Netflix', 'NFLX']))
print(scrape_headlines(nyt_business, ['Activision', 'ATVI']))
print(scrape_headlines(nyt_business, ['Apple', 'AAPL']))

print(scrape_headlines(bbc, ['Netflix', 'NFLX']))
print(scrape_headlines(bbc, ['Activision', 'ATVI']))
print(scrape_headlines(bbc, ['Apple', 'AAPL']))