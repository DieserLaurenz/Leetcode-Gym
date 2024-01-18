import json
import os
import re
import shelve

import chatgptapi_new
import leetcode_submitter


def read_json_file(file_path):
    with open(file_path, 'r') as json_file:
        return json.load(json_file)


def save_response(response_directory, response_filename, submission_response):
    with open(os.path.join(response_directory, response_filename), 'w') as file:
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


def process_snippet(prompt, subfolder_path, question, snippet, attempt, conversation_id):
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
        return True, "", ""
    elif attempt == 3:
        with shelve.open(cache_path) as cache:
            cache_key = f"{question_id}_{lang_slug}"
            cache[cache_key] = submission_response
    else:
        error_prompt = extract_info_and_generate_prompt(submission_response)
        print(f"Fehler-Prompt für Versuch {attempt + 1}: {error_prompt}")

        response_filename = f'response_{lang_slug}_{attempt}_failed.json'
        save_response(response_directory, response_filename, submission_response)
        return False, error_prompt, conversation_id


def generate_prompt_content(question, snippet):
    return (
        f'Solve the following problem in {snippet["lang"]}. '
        'Use the provided template as a starting point.\n\n'
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


def process_question(json_file_path, subfolder_path):
    question = read_json_file(json_file_path)

    for snippet in question["codeSnippets"]:
        attempt = 0
        conversation_id = None
        prompt = generate_prompt_content(question, snippet)
        while attempt < 3:
            is_success, error_prompt, conversation_id = process_snippet(prompt, subfolder_path, question, snippet,
                                                                        attempt, conversation_id)
            if is_success:
                break  # Beende die Schleife, wenn die Lösung akzeptiert wurde
            attempt += 1
            prompt = error_prompt


def process_subfolder(base_path, subfolder):
    subfolder_path = os.path.join(base_path, subfolder)
    json_file_path = os.path.join(subfolder_path, f'{subfolder}.json')
    response_directory = os.path.join(subfolder_path, 'responses')

    os.makedirs(response_directory, exist_ok=True)

    if not os.path.exists(json_file_path):
        return

    process_question(json_file_path, subfolder_path)


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
