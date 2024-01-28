import os

def file_ends_with(files, suffix):
    return any(file.endswith(suffix) for file in files)

def find_problematic_responses(base_directory):
    for root, dirs, files in os.walk(base_directory):
        if 'responses' in dirs:
            responses_dir = os.path.join(root, 'responses')

            # Durchsuchen aller Programmiersprachen-Unterordner in responses
            for lang_dir in os.listdir(responses_dir):
                lang_path = os.path.join(responses_dir, lang_dir)
                if os.path.isdir(lang_path):
                    files_in_lang = os.listdir(lang_path)
                    success_found = False
                    problem_detected = False

                    # Überprüfen, ob nach einem success-File ein failed-File kommt
                    for i in range(3):
                        success_suffix = f'_{i}_success.json'
                        failed_suffix = f'_{i}_failed.json'

                        if file_ends_with(files_in_lang, success_suffix):
                            success_found = True

                        if file_ends_with(files_in_lang, success_suffix) and file_ends_with(files_in_lang, failed_suffix):
                            problem_detected = True
                            break

                        if success_found and file_ends_with(files_in_lang, failed_suffix):
                            problem_detected = True
                            break

                    if problem_detected:
                        print(f"Problem in Ordner: {root}/{lang_dir}")
                        break  # Brechen Sie die Schleife ab, wenn ein Problem gefunden wurde

# Basisverzeichnis, von dem die Suche startet
base_directory = '.'  # Setzen Sie hier Ihren Basispfad
find_problematic_responses(base_directory)
