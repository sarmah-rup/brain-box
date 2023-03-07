import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests
from bs4 import BeautifulSoup
import openai
import random
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from string import punctuation


# Authenticate with OpenAI
openai.api_key = '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'

# Authenticate with Google Sheets API
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('key.json', scope)
client = gspread.authorize(creds)

# Open the sheet and select the first worksheet
sheet = client.open_by_key('1fKGDbK67rRvOYWGWhHW09zIOwistHl4BLmYTscRxf1Y').sheet1

# Define a list of URL patterns and corresponding regex patterns to extract text between "see all" and "comments"
url_patterns = [
    {"pattern": "thehindu.com", "regex": r'see all(.*?)comments'},
    {"pattern": "nature.com", "regex": r'Buy or subscribe(.*?)Access options'}
]

# Get the URLs from the sheet
urls = sheet.col_values(1)[1:]  # Exclude the header row

# Loop through the URLs, extract the title and description, and populate the corresponding columns in the sheet
for i, url in enumerate(urls):
    response = requests.get(url)
    html_content = response.content
    soup = BeautifulSoup(html_content, 'html.parser')
    text = soup.get_text()
    
    # Find the regex pattern to use for the current URL
    regex_pattern = None
    for pattern in url_patterns:
        if pattern["pattern"] in url:
            regex_pattern = pattern["regex"]
            break
    
    # If a regex pattern was found, extract the text between "see all" and "comments"
    if regex_pattern:
        result = re.search(regex_pattern, text, re.IGNORECASE | re.DOTALL)
        if result:
            text_between = result.group(1).strip()
        else:
            text_between = ""
    else:
        text_between = ""
    
    # Input paragraph to be summarized
    paragraph = text_between

    # Tokenize paragraph into sentences
    sentences = sent_tokenize(paragraph)

    # Tokenize words in each sentence and remove stopwords and punctuation
    stop_words = set(stopwords.words('english') + list(punctuation))
    word_tokens = [word.lower() for sent in sentences for word in word_tokenize(sent) if word.lower() not in stop_words]

    # Calculate word frequency
    word_frequency = nltk.FreqDist(word_tokens)

    # Get most frequent words
    most_frequent_words = [pair[0] for pair in word_frequency.most_common(1)]

    # Generate summary based on most frequent words
    summary = []
    for sentence in sentences:
        if any(word in sentence.lower() for word in most_frequent_words):
            summary.append(sentence)

    # Join summary sentences into a paragraph
    summary_paragraph = ' '.join(summary)
    print(url)
    print(len(text_between))
    print(len(summary_paragraph))

