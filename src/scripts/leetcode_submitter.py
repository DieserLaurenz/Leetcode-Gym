import logging
import os
import time

import requests
from dotenv import load_dotenv
from requests.exceptions import RequestException, HTTPError

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
            logging.error("Error: CSRF token or LEETCODE_SESSION not set in .env file")
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
        logging.error(f"Error creating session: {e}")
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
        logging.error(f"HTTP error occurred: {http_err}")
    except RequestException as req_err:
        logging.error(f"Error while sending request: {req_err}")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")

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
        logging.info("[REQUEST] Submitting question...")
        submit_question_response, status_code = send_request("POST", submit_problem_url, session, json_data=json_data)

        if not submit_question_response or status_code != 200:
            logging.warning(f"Request unsuccessful: {status_code}")
            logging.info(f"Retrying... ")
            time.sleep(RETRY_DELAY)
            continue
        else:
            break

    submission_id = submit_question_response.json().get("submission_id")
    logging.info(f"Submission ID: {submission_id}")

    while True:
        time.sleep(RETRY_DELAY)
        logging.info("[REQUEST] Checking submission...")
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


def main(problem_url, question_id, lang_slug, code):
    session = create_session()
    submission_response = submit_question(session,
                                          problem_url,
                                          question_id, lang_slug,
                                          code)

    return submission_response
