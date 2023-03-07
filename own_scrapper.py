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


num_articles = 20



# Scrape the links
links = []
while len(links) < num_articles:
    

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all the article links
    article_links = soup.find_all("div", class_="element row-element")

    # Extract the link, title and image for each article
    for article in article_links:
        link = article.find("a")["href"]
        title = article.find("h3").text.strip()
        img_url = article.find("img")["data-original"]
        links.append({"title": title, "url": link, "img_url": img_url})

    # Check if there are more articles to load
    more_button = soup.find("a", class_="small-link show-more")
    if more_button:
        url = "https://www.thehindu.com" + more_button["data-show-more"]
    else:
        break

# Print the links
#for link in links:
#    print(len(link))
print(len(links))
print(links)
