import datetime
import os
import re
import time

import pyperclip
import undetected_chromedriver as uc
from dotenv import load_dotenv
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait

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

    # Wait for the document.readyState to be complete
    WebDriverWait(driver, 10).until(lambda d: d.execute_script('return document.readyState') == 'complete')


def load_conversation(driver, conversation_id):
    driver.get(f"https://chat.openai.com/c/{conversation_id}")

    # Wait for the document.readyState to be complete
    WebDriverWait(driver, 10).until(lambda d: d.execute_script('return document.readyState') == 'complete')





def get_response(driver):
    message_stream = driver.find_elements(By.CSS_SELECTOR,
                                          '.result-streaming.markdown.prose.w-full.break-words.dark\\:prose-invert.light')

    thinking_dots = driver.find_elements(By.CSS_SELECTOR, '.result-thinking.relative')

    successful_responses = driver.find_elements(By.CSS_SELECTOR,
                                                '.markdown.prose.w-full.break-words.dark\\:prose-invert.light')

    extracted_codes = driver.find_elements(By.CSS_SELECTOR, '.p-4.overflow-y-auto')

    message_cap_errors = driver.find_elements(By.CSS_SELECTOR, '.flex.items-center.gap-6')

    network_error_responses = driver.find_elements(By.CSS_SELECTOR,
                                                   '.text-red-500.markdown.prose.w-full.break-words.dark\\:prose-invert.light')

    unusual_activity_responses = driver.find_elements(By.CSS_SELECTOR,
                                                      '.mb-2.py-2.px-3.border.text-gray-600.rounded-md.text-sm.dark\\:text-gray-100.border-red-500.bg-red-500\\:10')

    if thinking_dots or message_stream:
        return "generating", "", ""
    elif unusual_activity_responses:
        return "unusual_activity_error", "", ""
    elif network_error_responses:
        return "network_error", "", ""
    elif message_cap_errors:
        return "message_cap_error", message_cap_errors[-1].text, ""
    elif successful_responses:
        if len(extracted_codes) != len(successful_responses):
            return "codes_responses_unequal_error", "", ""

        last_response = successful_responses[-1].text

        if extracted_codes:
            last_extracted_code = extracted_codes[-1].text
            return "successful", last_response, last_extracted_code

        return "successful", last_response, ""
    else:
        return "unknown_error", "", ""


def send_message(driver, prompt, conversation_id=None):

    if conversation_id is None:
        create_new_conversation(driver)
    else:
        load_conversation(driver, conversation_id)

    time.sleep(2)

    text_area = driver.find_element(By.ID, "prompt-textarea")

    pyperclip.copy(prompt)

    text_area.click()

    time.sleep(2)

    action_chain = ActionChains(driver)
    action_chain.key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()  # Use Keys.COMMAND if you're on macOS


    """
    for part in prompt.split('\n'):
        text_area.send_keys(part)
        ActionChains(driver).key_down(Keys.SHIFT).key_down(Keys.ENTER).key_up(Keys.SHIFT).key_up(Keys.ENTER).perform()
    """
    
    time.sleep(2)

    text_area.send_keys(Keys.ENTER)

    time.sleep(2)

    while True:

        response_message, response_text, extracted_code = get_response(driver)

        if response_message == "generating":
            print("Generating response...")
            time.sleep(5)
            continue
        else:
            break

    current_url = driver.current_url

    conversation_id = current_url.rsplit('/', 1)[-1]

    return response_message, response_text, extracted_code, conversation_id


if __name__ == '__main__':
    driver = init_driver()

    time.sleep(5)

    conversation_id = send_message(driver, "Test")
