import requests
import json


# Define your API key and URL
API_KEY = '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'
API_URL = 'https://api.openai.com/v1/images/generations'

# Define your prompt, model, and other parameters
prompt = input("Enter text prompt: ")
model = 'image-alpha-001'
size = '512x512'
response_format = 'url'

# Define the request payload
payload = {
    'model': model,
    'prompt': prompt,
    'num_images': 1,
    'size': size,
    'response_format': response_format
}

# Make the API request and get the response
headers = {'Authorization': f'Bearer {API_KEY}'}
response = requests.post(API_URL, headers=headers, json=payload)
response_data = json.loads(response.text)
print(response_data)

