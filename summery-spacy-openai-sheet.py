import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests
from bs4 import BeautifulSoup
import pytextrank
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize
from string import punctuation
import openai
import re
import spacy
from spacy.lang.en.stop_words import STOP_WORDS
from string import punctuation
from collections import Counter
from heapq import nlargest
import random
import os   
import json
import time
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db


# Initialize Firebase Admin SDK
cred = credentials.Certificate("farmland-serviceAccount.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://farmland-c1ffa-default-rtdb.firebaseio.com/'
})

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
    {"pattern": "nature.com", "regex": r'View author publications(.*?)Related Articles'}
]

# Get the URLs from the sheet
urls = sheet.col_values(1)[1:]  # Exclude the header row



# Loop through the URLs, extract the title and description, and populate the corresponding columns in the sheet
for i, url in enumerate(urls):
    response = requests.get(url)
    html_content = response.content
    soup = BeautifulSoup(html_content, 'html.parser')
    text = soup.get_text()
    print(text)
    
    regex_pattern = r"([A-Za-z]+)? (\d{1,2})?,? (\d{4})?,? ?(\d{2})?:?(\d{2})? ?([ap]m)?"


    match = re.search(regex_pattern, text)
    if match:
        month = match.group(1)
        day = match.group(2)
        year = match.group(3)
        hour = match.group(4)
        minute = match.group(5)
        am_pm = match.group(6)
    publishing_date = f"{month} {day}, {year}, {hour}:{minute} {am_pm}"
    
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

    # load a spaCy model, depending on language, scale, etc.
    nlp = spacy.load("en_core_web_sm")
    # add PyTextRank to the spaCy pipeline
    nlp.add_pipe("textrank")

    doc = nlp(text)
    # examine the top-ranked phrases in the document
    print(url)
    print(len(text))
    print(len(text_between))
    #len(list(doc.sents))
    keyword = []
    stopwords = list(STOP_WORDS)
    pos_tag = ['PROPN', 'ADJ', 'NOUN', 'VERB']
    for token in doc:
        if(token.text in stopwords or token.text in punctuation):
            continue
        if(token.pos_ in pos_tag):
            keyword.append(token.text)
    freq_word = Counter(keyword)
    #print(freq_word.most_common(5)) 
    max_freq = Counter(keyword).most_common(1)[0][1]
    for word in freq_word.keys():  
            freq_word[word] = (freq_word[word]/max_freq)
    freq_word.most_common(5)  
    sent_strength={}
    for sent in doc.sents:
        for word in sent:
            if word.text in freq_word.keys():
                if sent in sent_strength.keys():
                    sent_strength[sent]+=freq_word[word.text]
                else:
                    sent_strength[sent]=freq_word[word.text]
    #print(sent_strength) 
    #print("")
    summarized_sentences = nlargest(3, sent_strength, key=sent_strength.get)
    #print(summarized_sentences) 
    final_sentences = [ w.text for w in summarized_sentences ]
    summary = ' '.join(final_sentences)
    print(len(summary))
    

    completions = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": f"*****text={summary}*****"},
            {"role": "system", "content": "**!!!make sure you have exact line break as I have provided, start the answer with Title:** "},
            {"role": "user", "content": "Please provide the following details for the *text* above: \n\n\n\nTitle: title for a news headline \n\nDescription: (5 lines in news description style) \n\nCountry in context: USA,China (can have more than one country, but one is preferred) \n\nIs it anti-govt or anti-system?: (Yes/No) \n\nCategory: sports, politics, etc. (dont give me only news) \n\ntags: (eg: Nepal, Politics, Government) max 3 tags, dont start with #- stop after tags, no more info required "},
        ]
    )


    # parse the response JSON string into a Python object

    message = completions.choices


    for response in message:
        # serialize the response object to a JSON string
        response_str = json.dumps(response)
        
        # parse the JSON string into a Python object
        response_obj = json.loads(response_str)

        # extract the "content" field from the "message" dictionary
        content = response_obj['message']['content']
        print(len(content))
        print(content)
        try:
            # try to split the message string by two newline characters
            title, description, country, anti_govt, category, tags = content.split('\n\n')
        except ValueError:
            # if a ValueError is raised, split the message string by one newline character instead
            title, description, country, anti_govt, category, tags = content.split('\n')
        

        likes = random.randint(100, 1500)
        sheet.update_cell(i+2, 2, title[7:])  # Update the title column (column 2) starting from row 2 (i+2)
        sheet.update_cell(i+2, 3, description[13:])  # Update the description column (column 3) starting from row 2 (i+2)
        sheet.update_cell(i+2, 4, country[20:])  # Update the country column (column 4) starting from row 2 (i+2)
        sheet.update_cell(i+2, 5, anti_govt[33:])  # Update the anti-govt/anti-system column (column 5) starting from row 2 (i+2)
        sheet.update_cell(i+2, 6, category[10:])  # Update the category column (column 6) starting from row 2 (i+2)
        sheet.update_cell(i+2, 7, likes)  # Update the likes column (column 7) starting from row 2 (i+2)
        #sheet.update_cell(i+2, 8, publisher_name[15:])  # Update the publisher name column (column 8) starting from row 2 (i+2)
        sheet.update_cell(i+2, 9, publishing_date)  # Update the publishing date column (column 9) starting from row 2 (i+2)
        sheet.update_cell(i+2, 10, tags[6:])  # Update the tags column (column 10) starting from row 2 (i+2)
        time.sleep(30)
    
    
 
    

