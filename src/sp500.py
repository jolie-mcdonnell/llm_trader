import requests
from bs4 import BeautifulSoup

# Define the URL of the Wikipedia page
url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"

# Send an HTTP GET request to the URL
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    # Parse the HTML content of the page using Beautiful Soup
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the table containing the S&P 500 components
    table = soup.find('table', {'class': 'wikitable'})

    # Initialize an empty list to store the tickers and names
    sp500_data = []

    # Iterate through the rows of the table
    for row in table.find_all('tr')[1:]:
        columns = row.find_all('td')
        ticker = columns[0].text.strip()
        name = columns[1].text.strip()
        sp500_data.append([ticker, name])

    # Print the list of S&P 500 tickers and names
    for item in sp500_data:
        print(item)

else:
    print("Failed to retrieve the webpage.")
