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

# extract the image URL from the HTML content using BeautifulSoup
# extract the URL of the featured image from the HTML content using BeautifulSoup
img_tag = soup.find('img', class_='wp-post-image')
if img_tag is None:
    print("No featured image found")
else:
    img_url = img_tag.get('src')
    if img_url is not None:
        print("Featured image URL:", img_url)
    else:
        print("No featured image URL found")
