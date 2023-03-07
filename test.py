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
from google.cloud import firestore
import os

import os






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

    doc = nlp(text_between)
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
            {"role": "user", "content": "Please provide the following details for the *text* above: \n\n\n\nTitle: title for a news headline \n\nDescription: (3 lines in news description style) \n\nCountry in context: USA,China (can have more than one country, but one is preferred) \n\nIs it anti-govt or anti-system?: (Yes/No) \n\nCategory: sports, politics, etc. (must have only one word, make it look like bews category) \n\ntags: (eg: Nepal, Politics, Government) max 3 tags, dont start with #- stop after tags, no more info required "},
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

        
        # Remove the "Country in context: " prefix from the country field
        country = country.replace("Country in context: ", "").strip()

        # Remove the "Tags: " prefix from the tags field
        tags = tags.replace("Tags: ", "").strip()

        # Convert the country field to a list of countries
        countries = [c.strip() for c in country.split(',')]

        # Convert the tags field to a list of tags
        tags_list = [t.strip() for t in tags.split(',')]
        
        # Use a service account
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "farmland-serviceAccount.json"

        # Initialize Firestore database
        db = firestore.Client()

        
        likes = random.randint(100, 1500)

        # formt the data to be written to the database
        category = category.lower().strip() # convert to lowercase and remove extra white spaces

        # define regular expression patterns for each category
        politics_pattern = re.compile(r"\bpolitics\b", re.IGNORECASE)
        business_pattern = re.compile(r"\bbusiness\b|\beconomy\b", re.IGNORECASE)
        technology_pattern = re.compile(r"\btech\b|\btechnology\b", re.IGNORECASE)
        health_pattern = re.compile(r"\bhealth\b|\bmedical\b", re.IGNORECASE)
        entertainment_pattern = re.compile(r"\bentertainment\b|\bcelebrity\b", re.IGNORECASE)
        science_pattern = re.compile(r"\bscience\b|\btechnology\b", re.IGNORECASE)
        sports_pattern = re.compile(r"\bsports\b|\bnews\b", re.IGNORECASE)
        education_pattern = re.compile(r"\beducation\b|\bschool\b", re.IGNORECASE)
        environment_pattern = re.compile(r"\benvironment\b|\bclimate\b", re.IGNORECASE)
        crime_pattern = re.compile(r"\bcrime\b|\blaw\b", re.IGNORECASE)
        travel_pattern = re.compile(r"\btravel\b|\btourism\b", re.IGNORECASE)
        fashion_pattern = re.compile(r"\bfashion\b|\bclothing\b", re.IGNORECASE)
        food_pattern = re.compile(r"\bfood\b|\bcuisine\b", re.IGNORECASE)
        arts_pattern = re.compile(r"\barts\b|\bculture\b", re.IGNORECASE)
        religion_pattern = re.compile(r"\breligion\b|\bfaith\b", re.IGNORECASE)

        # search for pattern matches in the text and categorize accordingly
        if politics_pattern.search(category):
            category = "Politics"
        elif business_pattern.search(category):
            category = "Business"
        elif technology_pattern.search(category):
            category = "Technology"
        elif health_pattern.search(category):
            category = "Health"
        elif entertainment_pattern.search(category):
            category = "Entertainment"
        elif science_pattern.search(category):
            category = "Science"
        elif sports_pattern.search(category):
            category = "Sports"
        elif education_pattern.search(category):
            category = "Education"
        elif environment_pattern.search(category):
            category = "Environment"
        elif crime_pattern.search(category):
            category = "Crime"
        elif travel_pattern.search(category):
            category = "Travel"
        elif fashion_pattern.search(category):
            category = "Fashion"
        elif food_pattern.search(category):
            category = "Food"
        elif arts_pattern.search(category):
            category = "Arts"
        elif religion_pattern.search(category):
            category = "Religion"
        else:
            category = "Other"



        # Check if the document already exists
        doc_ref = db.collection('newsCatagory').document(category)
        doc = doc_ref.get()
        if doc.exists:
            print(f"The document '{category}' already exists")
        else:
            # Create the document
            doc_ref.set({
                'category': category
            })
        doc_ref = db.collection('newsrush').document()
        doc_ref.set({
            'title': title[7:],
            'description': description[13:],
            'country': countries,
            'anti_govt': anti_govt[33:],
            'category': category,
            'likes': likes,
            'publishing_date': publishing_date,
            'tags': tags_list,
            'url': url,
            'category_ref' : db.collection('newsCatagory').document(category)
        })
        print("document created successfully")
    if len(summary) > 50:
       # Delete the row from the sheet
        sheet.delete_rows(i+2)  # Add 2 to the index to account for the header row and 0-indexing
        for i, url in enumerate(urls):
                # ... code to check if row needs to be deleted ...
                if i == len(urls) - 1:
                    sheet.delete_rows(i+1)
                    break  # exit the loop instead of using continue
                
        
    
    
 
    

