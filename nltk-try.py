import requests
from bs4 import BeautifulSoup
import nltk
nltk.download('punkt')
nltk.download('stopwords')
from nltk import sent_tokenize
from nltk.corpus import stopwords
from heapq import nlargest

# Set the URL to be scraped
url = input("Enter the URL to be scraped: ")

# Make a request to the website and get the HTML content
response = requests.get(url)
content = response.text

# Use BeautifulSoup to parse the HTML content and extract the text
soup = BeautifulSoup(content, 'html.parser')
text = soup.get_text()

# Tokenize the text into sentences and remove stop words
sentences = sent_tokenize(text)
stop_words = set(stopwords.words('english'))
filtered_sentences = [sentence for sentence in sentences if sentence.lower() not in stop_words]

# Calculate the word frequency of each sentence
word_frequencies = {}
for sentence in filtered_sentences:
    words = nltk.word_tokenize(sentence)
    for word in words:
        if word not in stop_words:
            if word not in word_frequencies.keys():
                word_frequencies[word] = 1
            else:
                word_frequencies[word] += 1

# Calculate the score of each sentence based on word frequency
sentence_scores = {}
for sentence in filtered_sentences:
    words = nltk.word_tokenize(sentence)
    for word in words:
        if word in word_frequencies.keys():
            if sentence not in sentence_scores.keys():
                sentence_scores[sentence] = word_frequencies[word]
            else:
                sentence_scores[sentence] += word_frequencies[word]

# Get the top 5 sentences with the highest score and generate a summary
summary_sentences = nlargest(5, sentence_scores, key=sentence_scores.get)
summary = ' '.join(summary_sentences)

print(summary)
