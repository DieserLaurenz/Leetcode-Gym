import os
import re

from dotenv import load_dotenv
from openai import OpenAI


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


def main(messages):
    api_key = load_config()
    if not api_key:
        print("API key not found. Please check your .env file.")
        return

    client = OpenAI(api_key=api_key)

    print("Getting ChatGPT Response...")
    answer = get_response(client, messages)
    return answer


if __name__ == "__main__":
    main()
