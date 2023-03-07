import requests
from bs4 import BeautifulSoup
import openai
from io import BytesIO
from requests.structures import CaseInsensitiveDict
import json
import io
import re





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

print(text)
      