from openai import OpenAI # type: ignore
import os
os.environ['OPENAI_API_KEY'] = ""
client = OpenAI()



def fetch_posts_gpt(  crypto_title , specific_date):
    today = datetime.now().strftime('%Y-%m-%d')

    # Define the prompt to fetch articles
    prompt = f"Give me the top 10 articles about {crypto_title} published on Nov 10th 2024. " \
             "Provide each article in the following format: 'Title: <article title>, URL: <url>, Date: <published date>'."

    # Call OpenAI's ChatGPT model
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": prompt}
        ],
        max_tokens=500
    )

    # Extract response text
    article_list = print(response.choices[0].message)
    return article_list
