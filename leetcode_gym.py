import datetime
import json
import os
import re
import shelve
import time

import pyperclip
from selenium.common import WebDriverException

import chatgpt_selenium_automation
import chatgptapi_new
import leetcode_submitter


def read_json_file(file_path):
    with open(file_path, 'r') as json_file:
        return json.load(json_file)


def save_response(response_directory, response_filename, submission_response, lang):
    lang_response_directory = os.path.join(response_directory, lang)

    if not os.path.exists(lang_response_directory):
        os.makedirs(lang_response_directory)

    with open(os.path.join(lang_response_directory, response_filename), 'w') as file:
        json.dump(submission_response, file, indent=4)


def extract_code(answer):
    lang_slugs = ['cpp', 'java', 'python', 'python3', 'c', 'csharp', 'javascript', 'typescript', 'php', 'swift',
                  'kotlin', 'dart', 'go', 'ruby', 'scala', 'rust', 'racket', 'erlang', 'elixir', 'scheme']

    for lang_slug in lang_slugs:
        pattern = rf"```{lang_slug}\n([\s\S]*?)\n```"
        match = re.search(pattern, answer)
        if match:
            return match.group(1)
    return None


def collect_code_input():
    print("Please paste your code. After pasting, hit Enter twice to finish.")
    code_lines = []
    while True:
        try:
            line = input()
            if line == '':
                # Check if the previous line was also empty (i.e., two consecutive Enters)
                if code_lines and code_lines[-1] == '':
                    code_lines.pop()  # Remove the last empty line
                    break
            code_lines.append(line)
        except EOFError:
            # Handle the case where the end of input is signaled by EOF (Ctrl+D)
            break

    return '\n'.join(code_lines)


def process_snippet_with_copy_to_clipboard(subfolder_path, question, snippet, attempt, conversation_id):
    lang_slug = snippet['langSlug']
    title_slug = question['titleSlug']
    question_id = question['questionId']
    cache_path = 'snippet_cache.db'
    response_directory = os.path.join(subfolder_path, 'responses')
    problem_url = f"https://leetcode.com/problems/{title_slug}"

    if check_cache(cache_path, question_id, lang_slug):
        print(f"Cache hit for {question_id} in {lang_slug}. Skipping.")
        return True, "", ""
    else:
        print(f"Processing: {title_slug} in {lang_slug}.")

    extracted_code = collect_code_input()

    submission_response = leetcode_submitter.main(problem_url, question_id, lang_slug, extracted_code)

    # Überprüfe, ob die Lösung akzeptiert wurde
    if submission_response.get("status_msg") == 'Accepted':
        with shelve.open(cache_path) as cache:
            cache_key = f"{question_id}_{lang_slug}"
            cache[cache_key] = submission_response

        response_filename = f'response_{lang_slug}_{attempt}_success.json'
        save_response(response_directory, response_filename, submission_response)
        print(f"Korrekte Antwort")
        return True, "", ""
    elif attempt == 3:
        print(f"Versuche überschritten")
        with shelve.open(cache_path) as cache:
            cache_key = f"{question_id}_{lang_slug}"
            cache[cache_key] = submission_response
    else:
        error_prompt = extract_info_and_generate_prompt(submission_response)
        print(f"Fehler-Antwort für Versuch {attempt + 1}")

        response_filename = f'response_{lang_slug}_{attempt}_failed.json'
        save_response(response_directory, response_filename, submission_response)
        return False, error_prompt, conversation_id


def extract_time(text):
    # Regular expression pattern to find time in the format HH:MM AM/PM
    time_pattern = re.compile(r'\b\d{1,2}:\d{2}\s*(AM|PM)\b')

    # Search for the pattern in the text
    time_match = time_pattern.search(text)

    if time_match:
        extracted_time = time_match.group()
        print(f"Extracted time: {extracted_time}")
        return extracted_time
    else:
        print("Time not found in the text.")
        return None


def calculate_sleep(time_str):
    # Parse the specified time
    time_format = "%I:%M %p"  # Format like '2:51 PM'
    specified_time = datetime.datetime.strptime(time_str, time_format)

    # Get the current time
    now = datetime.datetime.now()

    # Replace the year, month, and day of specified_time with current year, month, and day
    specified_time = specified_time.replace(year=now.year, month=now.month, day=now.day)

    # Check if the specified time is already passed for today
    if specified_time < now:
        # If so, set it to the next day
        specified_time += datetime.timedelta(days=1)

    # Calculate the sleep duration in seconds
    sleep_duration = (specified_time - now).total_seconds()

    # Return the sleep_duration
    return sleep_duration


def process_snippet_with_web_api(prompt, subfolder_path, question, snippet, attempt, conversation_id):
    lang_slug = snippet['langSlug']
    title_slug = question['titleSlug']
    question_id = question['questionId']
    cache_path = 'snippet_cache.db'
    response_directory = os.path.join(subfolder_path, 'responses')
    problem_url = f"https://leetcode.com/problems/{title_slug}"

    if lang_slug in ('python', 'python3'):
        print(f"Python. Skipping.")
        return True, "", ""

    if check_cache(cache_path, question_id, lang_slug):
        print(f"Cache hit for {question_id} in {lang_slug}. Skipping.")
        return True, "", ""
    else:
        print(f"Processing: {title_slug} in {lang_slug}.")

    answer, conversation_id = chatgptapi_new.send_message_with_SyncChatGPT(prompt, conversation_id)
    extracted_code = extract_code(answer)
    print(extracted_code)

    if not extracted_code:
        print("Kein Code gefunden")
        return False, "", ""

    submission_response = leetcode_submitter.main(problem_url, question_id, lang_slug, extracted_code)

    # Überprüfe, ob die Lösung akzeptiert wurde
    if submission_response.get("status_msg") == 'Accepted':
        with shelve.open(cache_path) as cache:
            cache_key = f"{question_id}_{lang_slug}"
            cache[cache_key] = submission_response

        response_filename = f'response_{lang_slug}_{attempt}_success.json'
        save_response(response_directory, response_filename, submission_response)
        print(f"Korrekte Antwort")
        return True, "", ""
    elif attempt == 3:
        print(f"Versuche überschritten")
        with shelve.open(cache_path) as cache:
            cache_key = f"{question_id}_{lang_slug}"
            cache[cache_key] = submission_response
    else:
        error_prompt = extract_info_and_generate_prompt(submission_response)
        print(f"Fehler-Antwort für Versuch {attempt + 1}")

        response_filename = f'response_{lang_slug}_{attempt}_failed.json'
        save_response(response_directory, response_filename, submission_response)
        return False, error_prompt, conversation_id


def process_snippet_with_selenium_method(prompt, subfolder_path, question, snippet, attempt, conversation_id, driver):
    lang_slug = snippet['langSlug']
    lang = snippet['lang']
    title_slug = question['titleSlug']
    question_id = question['questionId']
    cache_path = 'snippet_cache.db'
    response_directory = os.path.join(subfolder_path, 'responses')
    problem_url = f"https://leetcode.com/problems/{title_slug}"

    if lang_slug in ('python', 'python3'):
        print(f"Python. Skipping.")
        return True, "", ""

    if check_cache(cache_path, question_id, lang_slug):
        print(f"Cache hit for {question_id} in {lang_slug}. Skipping.")
        return True, "", ""
    else:
        print(f"Processing: {title_slug} in {lang_slug}.\nAttempt: {attempt}")

    response_message, response_text, extracted_code, conversation_id = chatgpt_selenium_automation.send_message(driver,
                                                                                                                prompt,
                                                                                                                conversation_id)

    if response_message == "message_cap_error":
        extracted_time = extract_time(response_text)
        time_to_sleep = calculate_sleep(extracted_time)
        print(response_message)
        print(f"Time to sleep: {time_to_sleep}")
        time.sleep(time_to_sleep + 60)
        return False, "", conversation_id
    elif response_message == "unusual_activity_error":

        print(response_message)
        time.sleep(5)
        return False, "", conversation_id
    elif response_message == "network_error":

        print(response_message)
        time.sleep(5)
        return False, "", conversation_id
    elif response_message == "unknown_error":

        print(response_message)
        time.sleep(5)
        return False, "", conversation_id
    elif extracted_code == "":

        print("No code found")
        time.sleep(5)
        return False, "", conversation_id

    submission_response = leetcode_submitter.main(problem_url, question_id, lang_slug, extracted_code)

    # Überprüfe, ob die Lösung akzeptiert wurde
    if submission_response.get("status_msg") == 'Accepted':
        with shelve.open(cache_path) as cache:
            cache_key = f"{question_id}_{lang_slug}"
            cache[cache_key] = submission_response

        response_filename = f'response_{lang_slug}_{attempt}_success.json'
        save_response(response_directory, response_filename, submission_response, lang)
        print(f"Korrekte Antwort in Versuch: {attempt}")
        return True, "", ""
    elif attempt == 3:
        print(f"Versuche überschritten")
        with shelve.open(cache_path) as cache:
            cache_key = f"{question_id}_{lang_slug}"
            cache[cache_key] = submission_response
    else:
        error_prompt = extract_info_and_generate_prompt(submission_response)
        print(f"Fehlerhafte Antwort in Versuch: {attempt}")

        response_filename = f'response_{lang_slug}_{attempt}_failed.json'
        save_response(response_directory, response_filename, submission_response, lang)
        return False, error_prompt, conversation_id


def generate_prompt_content(question, snippet):
    return (
        f'Solve the following problem in {snippet["lang"]}. '
        'Solely fill in the provided function template with the code and return it\n\n'  ## Hence common redecleration of the main function.
        f'Template:\n\n{snippet["code"]}\n\nProblem:\n\n{question["content"]}\n\n'
    )


def extract_info_and_generate_prompt(response):
    error_type = response['status_msg']

    # Initialize variables to store details
    test_input = response.get('last_testcase')
    output = response.get('code_output')
    expected_output = response.get('expected_output')
    testcases_passed = response.get('total_correct')
    total_testcases = response.get('total_testcases')

    # Format the test input if it contains newlines
    if test_input and "\n" in test_input:
        test_input = " ".join([f"Input {idx + 1}: {part}" for idx, part in enumerate(test_input.split('\n'))])

    # Handle different error types
    if error_type == "Compile Error":
        error_detail = response.get('full_compile_error', 'No detailed information available for compile error.')
    elif error_type == "Runtime Error":
        error_detail = response.get('full_runtime_error', 'No detailed information available for runtime error.')
    elif error_type == "Time Limit Exceeded":
        error_detail = f"Execution time of the code exceeded the time limit. \n\nTest cases passed: {testcases_passed}/{total_testcases}"
    elif error_type == "Wrong Answer":
        error_detail = f"Solution produced a wrong answer. Test cases passed: {testcases_passed}/{total_testcases}"
    elif error_type == "Memory Limit Exceeded":
        error_detail = f"Execution of the code exceeded the memory limit. \n\nTest cases passed: {testcases_passed}/{total_testcases}"
    else:
        error_detail = error_type

    # Construct the prompt with conditional inclusions
    prompt_parts = [
        f"This solution is not correct. See the following error details to improve on the code.\n\nError type:\n\n{error_type}\n\nError details:\n\n{error_detail}"]
    if test_input is not None:
        prompt_parts.append(f"\n\nLast executed input: {test_input}")
    if output is not None:
        prompt_parts.append(f"\n\nReceived output: {output}")
    if expected_output is not None:
        prompt_parts.append(f"\n\nExpected output: {expected_output}")

    return " ".join(prompt_parts)


def check_cache(cache_path, question_id, lang_slug):
    with shelve.open(cache_path) as cache:
        return cache.get(f"{question_id}_{lang_slug}") is not None


def process_question_with_copy_to_clipboard(json_file_path, subfolder_path):
    question = read_json_file(json_file_path)

    for snippet in question["codeSnippets"]:
        attempt = 0
        conversation_id = None
        prompt = generate_prompt_content(question, snippet)

        pyperclip.copy(prompt)
        print("Copied initial prompt to clipboard")

        while attempt < 3:
            is_success, error_prompt, conversation_id = process_snippet_with_copy_to_clipboard(subfolder_path, question,
                                                                                               snippet,
                                                                                               attempt, conversation_id)
            if is_success:
                break  # Beende die Schleife, wenn die Lösung akzeptiert wurde
            attempt += 1
            prompt = error_prompt

            pyperclip.copy(prompt)
            print("Copied error prompt to clipboard")


def process_question_with_selenium_method(json_file_path, subfolder_path, driver):
    question = read_json_file(json_file_path)

    for snippet in question["codeSnippets"]:
        attempt = 0
        conversation_id = None
        prompt = generate_prompt_content(question, snippet)

        while attempt < 3:
            is_success, error_prompt, conversation_id = process_snippet_with_selenium_method(prompt, subfolder_path,
                                                                                             question,
                                                                                             snippet,
                                                                                             attempt, conversation_id,
                                                                                             driver)
            if is_success:
                break  # Beende die Schleife, wenn die Lösung akzeptiert wurde
            else:
                if error_prompt == "":
                    print("Retrying to fetch the answer from ChatGPT...")
                    attempt = 0
                    conversation_id = None
                    continue
                else:
                    attempt += 1
                    prompt = error_prompt


def process_question_with_web_api(json_file_path, subfolder_path):
    question = read_json_file(json_file_path)

    for snippet in question["codeSnippets"]:
        attempt = 0
        conversation_id = None
        prompt = generate_prompt_content(question, snippet)

        while attempt < 3:
            is_success, error_prompt, conversation_id = process_snippet_with_web_api(prompt, subfolder_path, question,
                                                                                     snippet,
                                                                                     attempt, conversation_id)
            if is_success:
                break  # Beende die Schleife, wenn die Lösung akzeptiert wurde
            attempt += 1
            prompt = error_prompt


def process_subfolder(base_path, subfolder, chatgpt_mode, driver):
    subfolder_path = os.path.join(base_path, subfolder)
    json_file_path = os.path.join(subfolder_path, f'{subfolder}.json')
    response_directory = os.path.join(subfolder_path, 'responses')

    os.makedirs(response_directory, exist_ok=True)

    if not os.path.exists(json_file_path):
        return

    if chatgpt_mode == 0:
        process_question_with_copy_to_clipboard(json_file_path, subfolder_path)
    if chatgpt_mode == 1:
        process_question_with_selenium_method(json_file_path, subfolder_path, driver)
    if chatgpt_mode == 2:
        process_question_with_web_api(json_file_path, subfolder_path)


def process_folders(base_path, folders, chatgpt_mode, driver):
    for folder in folders:
        folder_path = os.path.join(base_path, folder)
        subfolders = [d for d in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, d))]
        for subfolder in subfolders:
            process_subfolder(folder_path, subfolder, chatgpt_mode, driver)


def access_questions(chatgpt_mode, driver):
    base_folders = ['Easy', 'Medium', 'Hard']
    process_folders('questions/', base_folders, chatgpt_mode, driver)


def is_driver_alive(driver):
    try:
        # A simple operation to check if the driver is still responsive
        driver.current_url
        return True
    except Exception:
        return False


def main():
    chatgpt_mode = int(input("Bitte gewünschten Modus eingeben: "))
    # 0: Copy to Clipboard, 1: Selenium Method, 2: ChatGPT Plus WEB Api Method, 3: ChatGPT API Method

    driver = None

    while True:
        try:

            if chatgpt_mode == 1:
                if not is_driver_alive(driver):
                    driver = chatgpt_selenium_automation.init_driver()

            access_questions(chatgpt_mode, driver)
            break  # Break the loop if everything went well

        except Exception as e:
            print(f"Ein Fehler ist aufgetreten: {e}")
            # Here, you can decide whether to retry or not
            print("Restarting the programm...")
            time.sleep(5)
            continue


main()
