import os
import time

from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from seleniumbase import Driver

load_dotenv()


def init_driver():
    chatgpt_session_token = os.getenv('CHATGPT_SESSION_TOKEN')

    driver = Driver(uc=True)

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


def get_response(driver, attempt):
    # Um DOM Abfragen zu reduzieren und somit Speicher effizienter zu nutzen
    all_elements = driver.find_elements(By.CSS_SELECTOR,
                                        '.result-streaming.markdown.prose.w-full.break-words.dark\\:prose-invert.light, ' +
                                        '.result-thinking.relative, ' +
                                        '.markdown.prose.w-full.break-words.dark\\:prose-invert.light, ' +
                                        '.flex.items-center.gap-6, ' +
                                        '.text-red-500.markdown.prose.w-full.break-words.dark\\:prose-invert.light, ' +
                                        '.mb-2.py-2.px-3.border.text-gray-600.rounded-md.text-sm.dark\\:text-gray-100.border-red-500.bg-red-500\\:10' +
                                        '.p-4.overflow-y-auto')

    message_stream = [el for el in all_elements if 'result-streaming' in el.get_attribute('class')]
    thinking_dots = [el for el in all_elements if 'result-thinking' in el.get_attribute('class')]
    successful_responses = [el for el in all_elements if
                            el.get_attribute('class') == 'markdown prose w-full break-words dark\\:prose-invert light']
    message_cap_errors = [el for el in all_elements if 'flex items-center gap-6' in el.get_attribute('class')]
    network_error_responses = [el for el in all_elements if 'text-red-500' in el.get_attribute('class')]
    unusual_activity_responses = [el for el in all_elements if 'mb-2 py-2 px-3 border' in el.get_attribute('class')]
    extracted_codes = [el for el in all_elements if '.p-4.overflow-y-auto' in el.get_attribute('class')]


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

        if attempt + 1 != len(extracted_codes):
            return "attempt_responses_unequal_error", "", ""

        last_response = successful_responses[-1].text

        if extracted_codes:
            last_extracted_code = extracted_codes[-1].text
            return "successful", last_response, last_extracted_code

        return "successful", last_response, ""
    else:
        return "unknown_error", "", ""


def send_message(driver, prompt, attempt, conversation_id=None):
    if conversation_id is None:
        create_new_conversation(driver)
    else:
        load_conversation(driver, conversation_id)

    text_area = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "prompt-textarea"))
    )
    text_area.click()

    time.sleep(0.7)

    driver.execute_script("arguments[0].value = arguments[1];", text_area, prompt)

    time.sleep(0.7)

    text_area.send_keys(Keys.ENTER)

    time.sleep(0.7)

    text_area.send_keys(Keys.ENTER)

    while True:
        time.sleep(5)

        response_message, response_text, extracted_code = get_response(driver, attempt)

        if response_message == "generating":
            print("Generating response...")
            continue
        else:
            break

    current_url = driver.current_url

    conversation_id = current_url.rsplit('/', 1)[-1]

    return response_message, response_text, extracted_code, conversation_id


if __name__ == '__main__':
    driver = init_driver()

    time.sleep(5)

    conversation_id = send_message(driver, "Test\nauf lock", 0)
