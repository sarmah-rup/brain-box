import requests
import pandas as pd
import csv

# set API endpoint and API key
endpoint = 'https://api.nytimes.com/svc/topstories/v2/'
api_key = 'tGMi1oP02aNLzwTwv6gMCXKvNDjHuRwZ'

# list of sections to query
sections = ['home', 'arts']

# list to store all articles
all_articles = []

# iterate through all sections and fetch articles
for section in sections:
    url = endpoint + section + '.json?api-key=' + api_key
    response = requests.get(url)
    data = response.json()

    # Extract the relevant fields from each article
articles = []
for article in data['results']:
    title = article['title']
    abstract = article['abstract']
    url = article['url']
    articles.append((title, abstract, url))

# Save the data to a CSV file
with open('articles.csv', 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Title', 'Abstract', 'URL'])
    writer.writerows(articles)