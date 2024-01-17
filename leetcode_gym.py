import os
import json
import re

import leetcode_submitter
import chatgptapi
import chatgptapi_new
import pyperclip

def read_json_file(file_path):
    with open(file_path, 'r') as json_file:
        return json.load(json_file)

def extract_code(answer):
    lang_slugs = ['cpp', 'java', 'python', 'python3', 'c', 'csharp', 'javascript', 'typescript', 'php', 'swift',
                  'kotlin', 'dart', 'go', 'ruby', 'scala', 'rust', 'racket', 'erlang', 'elixir', 'scheme']

    for lang_slug in lang_slugs:
        pattern = rf"```{lang_slug}\n([\s\S]*?)\n```"
        match = re.search(pattern, answer)
        if match:
            return match.group(1)
    return None

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

def process_subfolder(base_path, subfolder):
    subfolder_path = os.path.join(base_path, subfolder)
    json_file_path = os.path.join(subfolder_path, f'{subfolder}.json')
    prompt_directory = os.path.join(subfolder_path, 'prompts')
    response_directory = os.path.join(subfolder_path, 'responses')  # Added directory for responses

    os.makedirs(prompt_directory, exist_ok=True)
    os.makedirs(response_directory, exist_ok=True)  # Create the responses directory

    if not os.path.exists(json_file_path):
        return

    question = read_json_file(json_file_path)
    title_slug = question['titleSlug']
    question_id = question['questionId']
    problem_url = f"https://leetcode.com/problems/{title_slug}"
    print(f"Processing: {title_slug}")

    for snippet in question["codeSnippets"]:
        messages = []
        conversation_id = None
        response_counter = 1  # Initialize a counter for responses

        lang = snippet['lang']
        lang_slug = snippet['langSlug']
        prompt_content = (
            f'Solve the following problem in {lang}. '
            'Use the provided template as a starting point.\n\n'
            f'Template:\n\n{snippet["code"]}\n\nProblem:\n\n{question["content"]}\n\n'
        )

        print(f"Initial prompt: {prompt_content}")

        #messages.append({'role': 'user', 'content': prompt_content})

        for i in range(3):
            #answer = chatgptapi.main(messages)
            answer, conversation_id = chatgptapi_new.send_message(prompt_content, conversation_id)

            print(f"ChatGPT Antwort: {answer}")

            extracted_code = extract_code(answer)

            if extracted_code:
                print("Code erfolgreich extrahiert")
            else:
                print("Kein Code gefunden")

            #messages.append({'role': 'assistant', 'content': answer})

            submission_response = leetcode_submitter.main(problem_url, question_id, lang_slug, extracted_code)

            # Determine the filename based on success or failure
            response_status = "success" if submission_response["run_success"] and submission_response["status_msg"] == 'Accepted' else "failed"
            response_filename = f'response_{lang}_{response_counter}_{response_status}.json'

            # Increment the response counter
            response_counter += 1

            # Save the submission response
            with open(os.path.join(response_directory, response_filename), 'w') as file:
                json.dump(submission_response, file, indent=4)

            if submission_response["run_success"] == True:
                if submission_response["status_msg"] == 'Wrong Answer':
                    error_prompt = extract_info_and_generate_prompt(submission_response)
                elif submission_response["status_msg"] == 'Accepted':
                    print("The solution is correct")
                    break
                else:
                    print(f"Another error message: {submission_response['status_msg']}")
                    exit()
            else:
                error_prompt = extract_info_and_generate_prompt(submission_response)

            print("ChatGPT produced a wrong answer...")
            print(f"Error prompt: {error_prompt}")

            prompt_content = error_prompt



def process_folders(base_path, folders):
    for folder in folders:
        folder_path = os.path.join(base_path, folder)
        subfolders = [d for d in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, d))]
        for subfolder in subfolders:
            process_subfolder(folder_path, subfolder)


def access_questions():
    base_folders = ['Easy', 'Medium', 'Hard']
    process_folders('questions/', base_folders)

access_questions()