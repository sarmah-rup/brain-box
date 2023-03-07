import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests
from bs4 import BeautifulSoup
import openai
import random
import re

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
   

    
    prompt = f"Please provide the following details for this text: [{text_between}] \n\n\n\nTitle: title of the text \n\nDescription: (3 lines) \n\nCountry in context: USA,China (can have more than one country, but one is preferred) \n\nIs it anti-govt or anti-system?: (Yes/No) \n\nCategory: sports, politics, etc. (dont give me only news) \n\nPublisher name: \n\nPublishing date: \n\ntags: max 5 tags- stop after tags, no more info required **make sure you have exact line break as I have provided**"
    completions = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=200,
        n=1,
        stop=None,
        temperature=1,
    )
    message = completions.choices[0].text.strip()
    print(message)
    title, description, country, anti_govt, category, publisher_name, publishing_date, tags = message.split('\n\n')
    likes = random.randint(100, 1500)
    sheet.update_cell(i+2, 2, title[7:])  # Update the title column (column 2) starting from row 2 (i+2)
    sheet.update_cell(i+2, 3, description[13:])  # Update the description column (column 3) starting from row 2 (i+2)
    sheet.update_cell(i+2, 4, country[20:])  # Update the country column (column 4) starting from row 2 (i+2)
    sheet.update_cell(i+2, 5, anti_govt[33:])  # Update the anti-govt/anti-system column (column 5) starting from row 2 (i+2)
    sheet.update_cell(i+2, 6, category[10:])  # Update the category column (column 6) starting from row 2 (i+2)
    sheet.update_cell(i+2, 7, likes)  # Update the likes column (column 7) starting from row 2 (i+2)
    sheet.update_cell(i+2, 8, publisher_name[15:])  # Update the publisher name column (column 8) starting from row 2 (i+2)
    sheet.update_cell(i+2, 9, publishing_date[17:])  # Update the publishing date column (column 9) starting from row 2 (i+2)
    sheet.update_cell(i+2, 10, tags[6:])  # Update the tags column (column 10) starting from row 2 (i+2)