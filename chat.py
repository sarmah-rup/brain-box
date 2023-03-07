import openai
openai.api_key = "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"

def ask_openai(question, model):
    response = openai.Completion.create(
        engine=model,
        prompt=question,
        temperature=1,
        max_tokens=1000,
        n=1,
        stop=None,
        frequency_penalty=0,
        presence_penalty=0
    )

    answer = response.choices[0].text.strip()
    return answer

def main():
    model = "text-davinci-003"
    while True:
        question = input("You: ")
        if question.lower() == "quit":
            break
        answer = ask_openai(question, model)
        print("Bot:", answer)

if __name__ == "__main__":
    main()
