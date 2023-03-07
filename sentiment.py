import requests
from bs4 import BeautifulSoup
import openai
from io import BytesIO
from requests.structures import CaseInsensitiveDict
import json
import io





# Authenticate with OpenAI

openai.api_key = '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'

# get the URL of the news article
url = input("Enter the URL of the news article: ")

# fetch the HTML content of the news article
response = requests.get(url)
html_content = response.content

# extract the text from the HTML content using BeautifulSoup
soup = BeautifulSoup(html_content, 'html.parser')
text = soup.get_text()


# Use OpenAI's API to identify the title and description and remove junk text
model_engine = "text-davinci-003"
prompt = f"Please provide a title, country of context, publishing date, pro-government(yes/no), news publisher name and 3 line description(must complete the context) of the following text:\n{text}\nTitle: "
completions = openai.Completion.create(
    engine=model_engine,
    prompt=prompt,
    max_tokens=100,
    n=1,
    stop=None,
    temperature=1,
)
message = completions.choices[0].text.strip()


print(message)
