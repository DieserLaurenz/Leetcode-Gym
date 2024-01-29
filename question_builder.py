import json
import os


def read_json_file(file_path):
    with open(file_path, 'r') as json_file:
        return json.load(json_file)


def write_to_file(content, file_path, mode='w'):
    with open(file_path, mode) as file:
        file.write(content)


def process_subfolder(base_path, subfolder):
    subfolder_path = os.path.join(base_path, subfolder)
    json_file_path = os.path.join(subfolder_path, f'{subfolder}.json')
    prompt_directory = os.path.join(subfolder_path, 'prompts')

    os.makedirs(prompt_directory, exist_ok=True)
    if not os.path.exists(json_file_path):
        return

    question = read_json_file(json_file_path)
    title_slug = question['titleSlug']
    url_content = f'[InternetShortcut]\nURL=https://leetcode.com/problems/{title_slug}\n'

    write_to_file(url_content, os.path.join(subfolder_path, f"{title_slug}.url"))

    for snippet in question["codeSnippets"]:
        prompt_content = (
            f'Within the provided {snippet["lang"]} function template, solve the specified problem without defining '
            f'any external code or modifying structures outside the template.\n\n'
            f'Template:\n\n{snippet["code"]}\n\nProblem:\n\n{question["content"]}\n\n'
        )
        write_to_file(prompt_content, os.path.join(prompt_directory, f'{snippet["lang"]}.txt'))


def process_folders(base_path, folders):
    for folder in folders:
        folder_path = os.path.join(base_path, folder)
        subfolders = [d for d in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, d))]
        for subfolder in subfolders:
            process_subfolder(folder_path, subfolder)


def add_prompts_and_url_shortcut():
    base_folders = ['Easy', 'Medium', 'Hard']
    process_folders('questions/', base_folders)


add_prompts_and_url_shortcut()
