import json
import os
import time
import requests
import logging
from dotenv import load_dotenv
from requests.exceptions import RequestException, HTTPError
from colorama import Fore

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

    while True:
        logging.info(Fore.LIGHTCYAN_EX + "[REQUEST] Submitting question...")
        submit_question_response, status_code = send_request("POST", problem_url, session, json_data=json_data)

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

def main():
    while True:
        code = collect_code_input()

        session = create_session()
        submission_response = submit_question(session,
                                              "https://leetcode.com/problems/palindrome-rearrangement-queries/submit/",
                                              "3203", "javascript",
                                              code)

        if submission_response["run_success"] == True:
            if submission_response["status_msg"] == 'Wrong Answer':
                print(extract_info_and_generate_prompt(submission_response))
            else:
                # Might be correct, some cases may not be caught
                print("The solution is correct")
                break
        else:
            "Compile Error, Runtime Error, Time Limit Exceeded, Wrong Answer"

            """
            {
        "status_code": 14,
        "lang": "python",
        "run_success": false,
        "status_runtime": "N/A",
        "memory": 13368000,
        "question_id": "3208",
        "elapsed_time": 11009,
        "compare_result": "111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111110000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
        "code_output": "",
        "std_output": "",
        "last_testcase": "\"gxcfpjvomeristeuosooastuyrpvunyoalialnpofgitiiuvyavhezxrubsyoiobigdrbtrweralkoumtfinhehueaawsxtuawohkaafuefgfoulxhuuozfegruceggvuevivyooaruxuhfuovozowojdiieuodobualabcmarkniuaoozwicwuaylnnaebouaeeougiiodwcrgbjaruogakyoomocixuojiueofixesceutlkjeqxxcgggmoeennnriiouuszveeiehbiamernaqeujinuioipehdwuaiknuhiwbzuiiteolqoeuhesizjxisiaetaiuaoaiifeieifpiamyuxhaiivkalzweoapcuibuoxbupetbeoiuayroamsaluicouwsmoeeajrleeugwfqwiihehrouaceoqotxreijuqossuotuuijdzljwsojpejeiiiagkfpkaudyhrqpiiayyyouudclyuutuwuamrttcxbjbdvimuihtobyceoieesjrcutadayxwqoychquirokooejfuuauoiikexaurgoeuoiqsaauauzbfcaojueqfwoueiozcuasiveiuiabolploikiupyxecdnmuaorecbixwqteivorerfiilyubikhuezofefdpmjnaojjvvbwnueentypzmoragbuwojhasouewutcwhriuwwkiepvpacrahidbiieuaxudhjmljhujsisrecybtvydueaavtihmlhugxqoodsjouluqeforudkaiakokoihwbaiowuibjbuexueoamoaexdwecorjehieuixhfeuvilrwloatuqaiiuycpeyeecpsmuixzeaeoaeogielwuomauduijiaivffosoiltjjqeuufazctfuobhwypmigdveiagxuabuipqitxaolnz\"\n43",
        "expected_output": "230",
        "task_finish_time": 1705159207971,
        "task_name": "judger.judgetask.Judge",
        "finished": true,
        "total_correct": 560,
        "total_testcases": 684,
        "runtime_percentile": null,
        "status_memory": "N/A",
        "memory_percentile": null,
        "pretty_lang": "Python",
        "submission_id": "1145131369",
        "status_msg": "Time Limit Exceeded",
        "state": "SUCCESS"
    }
            """

            """
            {
        "status_code": 11,
        "lang": "python",
        "run_success": true,
        "status_runtime": "N/A",
        "memory": 13004000,
        "question_id": "3208",
        "elapsed_time": 11009,
        "compare_result": "001101000110011101111000001001001000000110010001000001101010001000011001111111000010001111000000010110011000010101111100001101011000010110010111101101011011010111011010011001011100001001000100000110001000000011100001100100011101001000111001111001010110000000100000001010110100000000011111011010001000000110011100001000001000001101001011001011011000100101011101100010001000000101000101000000001000101000000000101010101101010100010110100000011111000101101110100000000001001000000110010001010100100101100100100000000000000101010000100000000000000001000000110001100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
        "code_output": "1",
        "std_output": "1\n2\n0\n",
        "last_testcase": "\"baeyh\"\n2",
        "expected_output": "2",
        "task_finish_time": 1705159252883,
        "task_name": "judger.judgetask.Judge",
        "finished": true,
        "total_correct": 209,
        "total_testcases": 684,
        "runtime_percentile": null,
        "status_memory": "N/A",
        "memory_percentile": null,
        "pretty_lang": "Python",
        "submission_id": "1145131890",
        "input_formatted": "\"baeyh\", 2",
        "input": "\"baeyh\"\n2",
        "status_msg": "Wrong Answer",
        "state": "SUCCESS"
    }
            """

            """
            {
        "status_code": 15,
        "lang": "python",
        "run_success": false,
        "runtime_error": "Line 14: SyntaxError: invalid syntax",
        "full_runtime_error": "SyntaxError: invalid syntax\n           ^\n    vowels +\nLine 14  (Solution.py)",
        "status_runtime": "N/A",
        "memory": 6844000,
        "question_id": "3208",
        "elapsed_time": 14,
        "compare_result": "000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
        "code_output": "",
        "std_output": "",
        "last_testcase": "\"baeyh\"\n2",
        "expected_output": "2",
        "task_finish_time": 1705159362767,
        "task_name": "judger.judgetask.Judge",
        "finished": true,
        "total_correct": 0,
        "total_testcases": 684,
        "runtime_percentile": null,
        "status_memory": "N/A",
        "memory_percentile": null,
        "pretty_lang": "Python",
        "submission_id": "1145133248",
        "status_msg": "Runtime Error",
        "state": "SUCCESS"
    }
            """

            """
            {
        "status_code": 20,
        "lang": "erlang",
        "run_success": false,
        "compile_error": "Line 22: Char 1: function beautiful_substrings/6 already defined",
        "full_compile_error": "Line 22: Char 1: function beautiful_substrings/6 already defined\n%   22| beautiful_substrings(S, LengthS, K, Start, _, Count) when Start < LengthS ->\n%     | ^",
        "status_runtime": "N/A",
        "memory": 0,
        "question_id": "3208",
        "task_finish_time": 1705159469727,
        "task_name": "judger.judgetask.Judge",
        "finished": true,
        "total_correct": null,
        "total_testcases": null,
        "runtime_percentile": null,
        "status_memory": "N/A",
        "memory_percentile": null,
        "pretty_lang": "Erlang",
        "submission_id": "1145134433",
        "status_msg": "Compile Error",
        "state": "SUCCESS"
    }
            """
            """
            {"status_code": 12, "lang": "python", "run_success": false, "status_runtime": "N/A", "memory": 979952000, "question_id": "3243", "elapsed_time": 586, "compare_result": "11111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000", "code_output": "", "std_output": "", "last_testcase": "1829505\n1255574165\n7\n\"11223\"", "expected_output": "5470", "task_finish_time": 1705164048967, "task_name": "judger.judgetask.Judge", "finished": true, "total_correct": 227, "total_testcases": 932, "runtime_percentile": null, "status_memory": "N/A", "memory_percentile": null, "pretty_lang": "Python", "submission_id": "1145187763", "status_msg": "Memory Limit Exceeded", "state": "SUCCESS"}
            """

            print(extract_info_and_generate_prompt(submission_response))


if __name__ == "__main__":
    main()
