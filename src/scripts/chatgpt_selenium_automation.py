import os
import time

from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from seleniumbase import Driver

load_dotenv()

# List of required environment variables
required_vars = ['CSRF_TOKEN', 'LEETCODE_SESSION', 'CHATGPT_SESSION_TOKEN']

# Check each variable and raise an error if not found
for var in required_vars:
    if not os.getenv(var):
        raise Exception(f"{var} is not set in the .env file.")


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
    # Warte bis das Chatfenster offen ist
    """
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div[role="presentation"].flex.h-full.flex-col'))
        )
    except TimeoutException:
        return "timeout_error", "", ""
    """

    # Finde den übergeordneten Container
    container = driver.find_element(By.CSS_SELECTOR, 'div[role="presentation"].flex.h-full.flex-col')

    # Suche innerhalb dieses Containers nach den spezifischen Elementen
    message_stream = container.find_elements(By.CSS_SELECTOR,
                                             '.result-streaming.markdown.prose.w-full.break-words.dark\\:prose-invert.light')
    thinking_dots = container.find_elements(By.CSS_SELECTOR, '.result-thinking.relative')
    successful_responses = container.find_elements(By.CSS_SELECTOR,
                                                   '.markdown.prose.w-full.break-words.dark\\:prose-invert.light')
    extracted_codes = container.find_elements(By.CSS_SELECTOR, '.p-4.overflow-y-auto')
    message_cap_errors = container.find_elements(By.CSS_SELECTOR, '.flex.items-center.gap-6')
    network_error_responses = container.find_elements(By.CSS_SELECTOR,
                                                      '.text-red-500.markdown.prose.w-full.break-words.dark\\:prose-invert.light')
    unusual_activity_responses = container.find_elements(By.CSS_SELECTOR,
                                                         '.mb-2.py-2.px-3.border.text-gray-600.rounded-md.text-sm.dark\\:text-gray-100.border-red-500.bg-red-500\\:10')

    # Der Rest der Logik bleibt unverändert
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

    time.sleep(2)

    driver.execute_script("arguments[0].value = arguments[1];", text_area, prompt)

    time.sleep(2)

    text_area.send_keys(Keys.ENTER)

    time.sleep(2)

    text_area.send_keys(Keys.ENTER)

    while True:
        time.sleep(7.5)

        response_message, response_text, extracted_code = get_response(driver, attempt)

        if response_message == "generating":
            print("Generating response...")
            continue
        elif response_message == "timeout_error":
            print("Elements are not present... Reloading")
            driver.refresh()
        else:
            break

    current_url = driver.current_url

    conversation_id = current_url.rsplit('/', 1)[-1]

    return response_message, response_text, extracted_code, conversation_id


if __name__ == '__main__':
    driver = init_driver()

    time.sleep(5)

    conversation_id = send_message(driver, "Test\nauf lock", 0)
