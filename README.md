# **llm_trader**

**llm_trader** is an automated stock trading program that leverages the power of large language models (LLMs), like GPT, to make real-time investment decisions based on recent news. The program scrapes stock-related news headlines from **Google News** and **Finnhub**, processes them using GPT to generate short-term investment strategies (Buy, Sell, Do Nothing), and then executes the trades through the **Alpaca API**.

The trading strategy is based on [Can ChatGPT Forecast Stock Price Movements? Return Predictability and Large Language Models](https://arxiv.org/abs/2304.07619) by Alejandro Lopez-Lira and Yuehua Tang. 


### **Features**
- Scrapes recent stock-related news headlines from **Google News** and **Finnhub**.
- Uses **OpenAI GPT** to analyze the news and generate an investment strategy (Buy, Sell, or Do Nothing).
- Executes stock trades via **Alpaca** twice a day: once at market open and once at market close.
- Automates the article scraping, LLM-based decision-making, and trading workflows using **GitHub Actions**.

### **Creating Accounts and Generating API Keys**

To use **llm_trader**, you'll need to create accounts with **Alpaca**, **Finnhub**, and **OpenAI** to generate the required API keys. Follow the steps below to set up each account and obtain your API keys:

1. **Create an Alpaca Account**
   - Visit the [Alpaca website](https://alpaca.markets/) and sign up for a **paper trading account**.
   - Once registered, navigate to the **API section** of your Alpaca dashboard to generate your **API key** and **secret key**.

2. **Create a Finnhub Account**
   - Visit the [Finnhub website](https://finnhub.io/) and sign up for an account.
   - After signing up, go to the paper trading dashboard and obtain your **API key**.

3. **Create an OpenAI Account**
   - Visit the [OpenAI website](https://beta.openai.com/signup/) and create an account.
   - After signing up, go to the **API section** to generate your **OpenAI API key**. 
### **Installation**

To get started with **llm_trader**, follow these steps:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/jolie-mcdonnell/llm_trader.git
   cd llm_trader
   ```
2. **Create a Virtual Environemnt and Install Required Dependencies:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   pip install -r requirements.txt
   ```
3. **Set up environment variables:**
   You will need to create a paper trading account with Alpaca and obtain your API keys. Set the following environment variables in GitHub Secrets or in a .env file:
   - ALPACA_API_KEY: Your Alpaca API key for paper trading.
   - ALPACA_SECRET_KEY: Your Alpaca secret API key.
   - OPENAI_API_KEY: Your OpenAI GPT API key.
   - FINNHUB_API_KEY: Your Finnhub API key.
4. **Configure GitHub Actions Workflow:**
  This repository is set up to run the automated tasks using GitHub Actions. Ensure your repository’s secrets are set correctly, and the workflow will run twice per day to trigger scraping, decision-making, and trade execution.

### **How it Works**

1. **Scraping News**  
   The program scrapes stock-related headlines from two sources:
   - **Google News**: Uses **BeautifulSoup** and the **Google News API** to gather relevant news headlines.
   - **Finnhub**: Uses the **Finnhub API** to collect more precise stock-related news.

2. **Processing News with GPT**  
   The scraped headlines are processed by **OpenAI GPT-3/4** to generate an investment strategy. GPT analyzes the sentiment, relevance, and potential impact of the headlines to create one of the following strategies: **Buy**, **Sell**, **Do Nothing**.

3. **Executing Trades**  
   Once the strategy is determined, the program executes the trade using the **Alpaca API**. Trades are made based on the strategy generated by GPT. The execution happens twice daily:
   - **At Market Open**: Typically around **9:30 AM EST**.
   - **At Market Close**: Typically around **4:00 PM EST**.
   - The trades are rebalanced every day at market close.

4. **Automation with GitHub Actions**  
   The entire process is automated using **GitHub Actions**, which triggers the tasks throughout the day.

   This automation ensures that the system stays up-to-date with the latest market data and continuously executes trades according to the evolving market conditions.


### **Results**
In practice, the algorithm did not perform nearly as well as reported in the article, but it was a fun project in algorithmic trading!


