from openai import OpenAI
import os

def generate_stock_recommendation(headline, company_name, term):
    # Set your OpenAI API key

    client = OpenAI()
    OpenAI.api_key = os.getenv('OPENAI_API_KEY')

    # Define the prompt for OpenAI API
    prompt = f"Forget all your previous instructions. Pretend you are a financial expert. You are a financial expert with stock recommendation experience. Answer only one word: 'YES' if good news, 'NO' if bad news, or 'UNKNOWN' if uncertain. Is this headline good or bad for the stock price of {company_name} in the {term} term? Headline: {headline}"

    # Call OpenAI API
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",  # Use the chat model
        messages=[
            {"role": "system", "content": "You are a financial expert with stock recommendation experience."},
            {"role": "user", "content": prompt}
        ]
    )

    result = response.choices[0].message.content

    # Return the recommendation
    return result

# TODO: REMOVE 
if __name__ == "__main__":
    # Example usage
    headline = "In Search of Cash, Studios Send Old Shows Back to Netflix"
    company_name = "Netflix"
    term = "short"

    result = generate_stock_recommendation(headline, company_name, term)

    print(f"Recommendation: {result}")
