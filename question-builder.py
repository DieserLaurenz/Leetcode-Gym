import json
import os

def read_question(path_to_json):
    """
    Read a JSON file and return its content.
    """
    with open(path_to_json, 'r') as json_file:
        return json.load(json_file)

def write_prompt(lang, code_snippet, content, prompt_directory):
    """
    Write the prompt information to a file in the specified directory.
    """
    prompt_path = os.path.join(prompt_directory, f'{lang}.txt')
    prompt_content = (
        f'Solve the following problem in {lang}. '
        'Use the provided template as a starting point.\n\n'
        f'Template:\n\n{code_snippet}\n\nProblem:\n\n{content}\n\n'
    )

    with open(prompt_path, 'w') as prompt_file:
        prompt_file.write(prompt_content)


def write_internet_shortcut(url, filename):
    """
    Creates an internet shortcut (.url file) with the given URL.

    Parameters:
    url (str): The URL for the shortcut.
    filename (str): The filename for the shortcut file, including the .url extension.
    """
    with open(filename, 'w') as file:
        file.write('[InternetShortcut]\n')
        file.write(f'URL={url}\n')


def process_subfolder(folder_path, subfolder):
    """
    Process each subfolder by reading the question and writing prompts.
    """
    subfolder_path = os.path.join(folder_path, subfolder)
    json_file_path = os.path.join(subfolder_path, f'{subfolder}.json')
    prompt_directory = os.path.join(subfolder_path, 'prompts')
    os.makedirs(prompt_directory, exist_ok=True)

    if os.path.exists(json_file_path):
        question = read_question(json_file_path)

        title_slug = question['titleSlug']

        url_file_path = os.path.join(subfolder_path, f"{question['titleSlug']}.url")
        write_internet_shortcut(f"https://leetcode.com/problems/{title_slug}", url_file_path)

        for snippet in question["codeSnippets"]:
            write_prompt(snippet["lang"], snippet["code"], question["content"], prompt_directory)

def process_folders(base_path, folders):
    """
    Process each base folder and its subfolders.
    """
    for folder in folders:
        folder_path = os.path.join(base_path, folder)
        subfolders = [d for d in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, d))]
        for subfolder in subfolders:
            process_subfolder(folder_path, subfolder)

def add_prompts_to_questions():
    base_folders = ['Easy', 'Medium', 'Hard']
    base_path = 'questions/'
    process_folders(base_path, base_folders)

add_prompts_to_questions()
