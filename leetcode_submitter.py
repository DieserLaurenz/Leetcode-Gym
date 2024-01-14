import json
import os
import time
import requests
import logging
from dotenv import load_dotenv
from requests.exceptions import RequestException, HTTPError
from colorama import Fore
import pyperclip

RETRY_DELAY = 2

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables
load_dotenv()


def create_session():
    """
    Create a new session object with loaded cookies.
    """
    try:
        session = requests.Session()
        csrf_token = os.getenv('CSRF_TOKEN')
        leetcode_session = os.getenv('LEETCODE_SESSION')

        if not csrf_token or not leetcode_session:
            logging.error(Fore.LIGHTRED_EX + "Error: CSRF token or LEETCODE_SESSION not set in .env file")
            exit()

        session.headers.update({
            'referer': 'https://leetcode.com/problems/check-if-array-is-good/',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'x-csrftoken': csrf_token,
        })

        session.cookies.update({
            'csrftoken': csrf_token,
            'LEETCODE_SESSION': leetcode_session
        })

        return session

    except Exception as e:
        logging.error(Fore.LIGHTRED_EX + f"Error creating session: {e}")
        exit()


def send_request(method, url, session, json_data=None):
    """
    Send a request using the given session.
    """
    try:
        if method == "GET":
            response = session.get(url, timeout=5, json=json_data)
        elif method == "POST":
            response = session.post(url, timeout=5, json=json_data)
        else:
            logging.error("Invalid method")
            return None, None

        response.raise_for_status()
        return response, response.status_code

    except HTTPError as http_err:
        logging.error(Fore.LIGHTRED_EX + f"HTTP error occurred: {http_err}")
    except RequestException as req_err:
        logging.error(Fore.LIGHTRED_EX + f"Error while sending request: {req_err}")
    except Exception as e:
        logging.error(Fore.LIGHTRED_EX + f"Unexpected error: {e}")

    return None, None


def submit_question(session, problem_url, question_id, lang, code):
    """
    Submit a question to LeetCode and check the response.
    """
    json_data = {
        'lang': lang,
        'question_id': question_id,
        'typed_code': code,
    }

    submit_problem_url = f"{problem_url}/submit/"

    while True:
        logging.info(Fore.LIGHTCYAN_EX + "[REQUEST] Submitting question...")
        submit_question_response, status_code = send_request("POST", submit_problem_url, session, json_data=json_data)

        if not submit_question_response or status_code != 200:
            logging.warning(f"Request unsuccessful: {status_code}")
            logging.info(f"Retrying... ")
            time.sleep(RETRY_DELAY)
            continue
        else:
            break

    submission_id = submit_question_response.json().get("submission_id")
    logging.info(Fore.LIGHTCYAN_EX + f"Submission ID: {submission_id}")

    while True:
        time.sleep(RETRY_DELAY)
        logging.info(Fore.LIGHTCYAN_EX + "[REQUEST] Checking submission...")
        submission_status_response, status_code = send_request("GET",
                                                               f"https://leetcode.com/submissions/detail/{submission_id}/check/",
                                                               session)

        if not submission_status_response or status_code != 200:
            logging.warning(f"Request unsuccessful: {status_code}")
            logging.info(f"Retrying... ")
            time.sleep(RETRY_DELAY)
            continue
        else:
            submission_status = submission_status_response.json()

            if submission_status.get("state") in ["PENDING", "STARTED"]:
                logging.info(f"Status: {submission_status['state']}")
                continue
            else:
                return submission_status


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


def main(problem_url, question_id, lang_slug):
    for i in range(3):
        code = collect_code_input()

        session = create_session()
        submission_response = submit_question(session,
                                              problem_url,
                                              question_id, lang_slug,
                                              code)

        print(submission_response)

        if submission_response["run_success"] == True:
            if submission_response["status_msg"] == 'Wrong Answer':
                error_prompt = extract_info_and_generate_prompt(submission_response)
            elif submission_response["status_msg"] == 'Accepted':
                # Might be correct, some cases may not be caught
                print("The solution is correct")
                return
            else:
                print(f"Another error message: {submission_response['status_msg']}")
                return
        else:
            error_prompt = extract_info_and_generate_prompt(submission_response)

        pyperclip.copy(error_prompt)
        print("The error prompt has been copied to clipboard")


if __name__ == "__main__":
    main()
