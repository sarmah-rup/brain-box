import os
import openai

# Load your API key from an environment variable or secret management service
openai.api_key = os.getenv("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")

response = openai.Completion.create(model="text-davinci-003", prompt="Say this is a test", temperature=0, max_tokens=7)