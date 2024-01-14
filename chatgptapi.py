import os
import re
import time
from openai import OpenAI
from dotenv import load_dotenv
import pyperclip

def load_config():
    load_dotenv(".env")
    return os.getenv("OPENAI_API_KEY")

def get_response(client, messages):
    response = client.chat.completions.create(
        messages=messages,
        model="gpt-4-1106-preview",  # Verify the model name
        temperature=0,
        max_tokens=1024,
        n=1,
        stop=None
    )
    return response.choices[0].message.content

def extract_code(lang_slugs, answer):
    for lang_slug in lang_slugs:
        pattern = rf"```{lang_slug}\n([\s\S]*?)\n```"
        match = re.search(pattern, answer)
        if match:
            return match.group(1)
    return None

def main():
    api_key = load_config()
    if not api_key:
        print("API key not found. Please check your .env file.")
        return

    client = OpenAI(api_key=api_key)
    messages = []
    lang_slugs = ['cpp', 'java', 'python', 'python3', 'c', 'csharp', 'javascript', 'typescript', 'php', 'swift',
                  'kotlin', 'dart', 'go', 'ruby', 'scala', 'rust', 'racket', 'erlang', 'elixir', 'scheme']

    while True:
        user_input = input("Bitte Prompt eingeben (type 'quit' to exit): ")
        if user_input == 'quit':
            break

        messages.append({'role': 'user', 'content': user_input})
        answer = get_response(client, messages)
        extracted_code = extract_code(lang_slugs, answer)

        if extracted_code:
            print("Extrahierter Code:\n", extracted_code)
            pyperclip.copy(extracted_code)
            print("Code zur Zwischenablage hinzugefügt")
        else:
            print("Kein Code gefunden")



        messages.append({'role': 'assistant', 'content': answer})

if __name__ == "__main__":
    main()
