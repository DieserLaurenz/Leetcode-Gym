import os
import time

import pyperclip
import undetected_chromedriver as uc
from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains


load_dotenv()


def init_driver():
    chatgpt_session_token = os.getenv('CHATGPT_SESSION_TOKEN')
    # Initialize the undetected Chrome driver
    options = uc.ChromeOptions()
    # You can add additional Chrome options here if needed
    driver = uc.Chrome(options=options)

    driver.get("https://chat.openai.com/?model=gpt-4")

    # Add the cookie
    driver.add_cookie({
        'name': '__Secure-next-auth.session-token',
        'value': chatgpt_session_token,
        'secure': True,
        'httpOnly': True,
        'path': '/'
    })

    time.sleep(1)

    driver.get("https://chat.openai.com/?model=gpt-4")

    # Wait for the document.readyState to be complete
    WebDriverWait(driver, 10).until(lambda d: d.execute_script('return document.readyState') == 'complete')

    return driver


def create_new_conversation(driver):
    driver.get("https://chat.openai.com/?model=gpt-4")


def load_conversation(driver, conversation_id):
    driver.get(f"https://chat.openai.com/c/{conversation_id}")

    # Wait for the document.readyState to be complete
    WebDriverWait(driver, 10).until(lambda d: d.execute_script('return document.readyState') == 'complete')


def send_message(driver, prompt, conversation_id=None):
    if conversation_id is None:
        create_new_conversation(driver)
    else:
        load_conversation(driver, conversation_id)

    text_area = driver.find_element(By.ID, "prompt-textarea")

    for part in prompt.split('\n'):
        text_area.send_keys(part)
        ActionChains(driver).key_down(Keys.SHIFT).key_down(Keys.ENTER).key_up(Keys.SHIFT).key_up(Keys.ENTER).perform()

    print("Done")

    time.sleep(2)

    text_area.send_keys(Keys.ENTER)

    time.sleep(5)

    while driver.find_elements(By.CSS_SELECTOR, '.result-thinking.relative'):
        print("Dot appeared")
        time.sleep(5)

    while driver.find_elements(By.CSS_SELECTOR,
                               '.result-streaming.markdown.prose.w-full.break-words.dark\\:prose-invert.light'):
        print("Is Streaming")
        time.sleep(5)

    print("Streaming ended")

    responses = driver.find_elements(By.CSS_SELECTOR, '.markdown.prose.w-full.break-words.dark\\:prose-invert.light')

    extracted_codes = driver.find_elements(By.CSS_SELECTOR, '.p-4.overflow-y-auto')

    print(f"Letzte Antwort:\n\n {responses[-1].text}")

    print("\n")

    print(f"Extrahierter Code:\n\n {extracted_codes[-1].text}")

    current_url = driver.current_url

    conversation_id = current_url.rsplit('/', 1)[-1]

    pyperclip.copy(extracted_codes[-1].text)

    return conversation_id


driver = init_driver()

time.sleep(5)

create_new_conversation(driver)

conversation_id = send_message(driver, "Test")
