from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from bs4 import BeautifulSoup
import requests

url = 'https://www.thehindu.com/news/national/manisha-saxena-appointed-director-general-of-tourism-meenakshi-negi-named-member-secretary-ncw/article66580450.ece'

# set up the browser using selenium
service = ChromeService(executable_path='path/to/chromedriver') # replace with actual path to chromedriver
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
driver = webdriver.Chrome(service=service, options=options)

# load the webpage
driver.get(url)
soup = BeautifulSoup(driver.page_source, 'html.parser')

# scrape all image tags
image_tags = soup.find_all('img')

# scrape all source tags with srcset
source_tags = soup.find_all('source', {'srcset': True})

# add the source urls to the image urls list
image_urls = []
for source in source_tags:
    image_urls.append(source['srcset'].split(' ')[0])
   

# add the image urls from img tags
for img in image_tags:
    print(img)
    print(img.attrs)
    image_urls.append(img['src'])


# find the url with the highest dimension
max_size = 0
max_url = ''
for url in image_urls:
    try:
        response = requests.get(url, stream=True)
        size = int(response.headers['content-length'])
        if size > max_size:
            max_size = size
            max_url = url
    except:
        continue

print("All image URLs:")
print(image_urls)
print("URL of the image with the highest dimensions:")
print(max_url)
