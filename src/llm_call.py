from openai import OpenAI
import os


def generate_stock_recommendation(headline, company_name, term):
    """
    The generate_stock_recommendation function takes in a headline, company name, and term (short or long) as arguments.
    It then uses the OpenAI API to generate a recommendation for whether the stock price of that company will go up or down based on that headline.
    The function returns 1 if it thinks the stock price will go up, -1 if it thinks it will go down, and 0 if it is uncertain.

    :param headline: Tthe headline of a news article
    :param company_name: The company to assess
    :param term: The time frame of the recommendation
    :return: A recommendation
    """
    # Set your OpenAI API key

    client = OpenAI()
    OpenAI.api_key = os.getenv("OPENAI_API_KEY")

    # Define the prompt for OpenAI API
    prompt = f"Forget all your previous instructions. Pretend you are a financial expert. You are a financial expert with stock recommendation experience. Answer only one word: 'YES' if good news, 'NO' if bad news, or 'UNKNOWN' if uncertain. Is this headline good or bad for the stock price of {company_name} in the {term} term? Headline: {headline}"

    # Call OpenAI API
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",  # Use the chat model
        messages=[
            {
                "role": "system",
                "content": "You are a financial expert with stock recommendation experience.",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
    )

    result_text = response.choices[0].message.content

    # Replace "YES" with 1, "NO" with -1, and "UNKNOWN" with 0
    if result_text == "YES":
        result = 1
    elif result_text == "NO":
        result = -1
    else:
        result = 0
    # print(headline)
    # print(company_name)
    # print(result_text)
    # print(result)
    # Return the recommendation
    return result


# # for testing
# headline = "Lead Levels in Children’s Applesauce May Be Traced to Cinnamon Additive"
# company_name = "Apple"
# term = "short"
# result = generate_stock_recommendation(headline, company_name, term)
# print(f"Recommendation: {result}")
