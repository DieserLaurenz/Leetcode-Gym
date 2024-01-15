import os
import json
import leetcode_submitter
import chatgptapi
import pyperclip

def read_json_file(file_path):
    with open(file_path, 'r') as json_file:
        return json.load(json_file)

def process_subfolder(base_path, subfolder):
    subfolder_path = os.path.join(base_path, subfolder)
    json_file_path = os.path.join(subfolder_path, f'{subfolder}.json')
    prompt_directory = os.path.join(subfolder_path, 'prompts')

    os.makedirs(prompt_directory, exist_ok=True)

    if not os.path.exists(json_file_path):
        return

    question = read_json_file(json_file_path)
    title_slug = question['titleSlug']
    question_id = question['questionId']
    problem_url = f"https://leetcode.com/problems/{title_slug}"
    print(f"Processing: {title_slug}")

    for snippet in question["codeSnippets"]:
        lang = snippet['lang']
        lang_slug = snippet['langSlug']
        prompt_content = (
            f'Solve the following problem in {lang}. '
            'Use the provided template as a starting point.\n\n'
            f'Template:\n\n{snippet["code"]}\n\nProblem:\n\n{question["content"]}\n\n'
        )
        pyperclip.copy(prompt_content)
        print(f"Copied prompt for {lang}")

        leetcode_submitter.main(problem_url, question_id, lang_slug)



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