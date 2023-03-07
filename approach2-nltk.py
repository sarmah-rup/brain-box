import urllib.request
from bs4 import BeautifulSoup
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords
from heapq import nlargest
import urllib.request





# Retrieve the article URL
url = input("Enter the URL of the news article: ")
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
}

req = urllib.request.Request(url, headers)
response = urllib.request.urlopen(req).read().decode('utf8', 'ignore')

# Retrieve the HTML content of the article
page = urllib.request.urlopen(url).read().decode('utf8', 'ignore')

# Parse the HTML content using BeautifulSoup
soup = BeautifulSoup(page, 'html.parser')

# Extract the article content
text = ' '.join(map(lambda p: p.text, soup.find_all('article')))

# Tokenize the article content into sentences
sentences = sent_tokenize(text)

# Remove stop words from the sentences
stop_words = set(stopwords.words('english'))
word_frequencies = {}
for word in text.split():
    if word.casefold() not in stop_words:
        if word not in word_frequencies:
            word_frequencies[word] = 1
        else:
            word_frequencies[word] += 1

# Calculate the weighted frequencies of the sentences
sentence_scores = {}
for sent in sentences:
    for word in sent.split():
        if word in word_frequencies:
            if len(sent.split()) < 30:
                if sent not in sentence_scores:
                    sentence_scores[sent] = word_frequencies[word]
                else:
                    sentence_scores[sent] += word_frequencies[word]

# Retrieve the top sentences based on their scores
summary_sentences = nlargest(5, sentence_scores, key=sentence_scores.get)

# Print the summary
print('\n\n'.join(summary_sentences))
