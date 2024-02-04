import os
import json
import shelve

import os

def file_ends_with(files, suffix):
    return any(file.endswith(suffix) for file in files)

def find_failed_after_success(base_directory):
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

                        if success_found and file_ends_with(files_in_lang, failed_suffix):
                            problem_detected = True
                            break

                    if problem_detected:
                        print(f"Problem in Ordner: {root}/{lang_dir}")
                        # Cache-Schlüssel von irgendeiner Datei im Verzeichnis extrahieren
                        sample_file_path = os.path.join(lang_path, files_in_lang[0])
                        # Cache löschen, wenn vorhanden
                        try:
                            with open(sample_file_path, 'r') as file:
                                data = json.load(file)
                                question_id = data.get('question_id')
                                lang_slug = data.get('lang')
                                cache_key = f"{question_id}_{lang_slug}"
                                with shelve.open(cache_path) as cache:
                                    if cache_key in cache:
                                        del cache[cache_key]
                                        print(f"Cache für {cache_key} entfernt.")
                        except Exception as e:
                            print(f"Fehler beim Lesen von {sample_file_path} oder beim Zugriff auf den Cache: {e}")
                        break  # Brechen Sie die Schleife ab, wenn ein Problem gefunden wurde


def find_problematic_responses(base_directory, cache_path):
    for root, dirs, files in os.walk(base_directory):
        if 'responses' in dirs:
            responses_dir = os.path.join(root, 'responses')

            # Durchsuchen aller Programmiersprachen-Unterordner in responses
            for lang_dir in os.listdir(responses_dir):
                lang_path = os.path.join(responses_dir, lang_dir)
                if os.path.isdir(lang_path):
                    files_in_lang = os.listdir(lang_path)
                    codes = set()

                    # Überprüfen, ob 'code' doppelt vorkommt
                    for file_name in files_in_lang:
                        if file_name.endswith('.json'):
                            with open(os.path.join(lang_path, file_name), 'r') as file:
                                data = json.load(file)
                                code = data.get('code')
                                question_id = data.get('question_id')
                                lang_slug = data.get('lang')

                                if code and code in codes:
                                    print(f"Doppelter 'code' gefunden in: {root}/{lang_dir}")
                                    # Cache löschen, wenn vorhanden
                                    cache_key = f"{question_id}_{lang_slug}"
                                    with shelve.open(cache_path) as cache:
                                        if cache_key in cache:
                                            del cache[cache_key]
                                            print(f"Cache für {cache_key} entfernt.")
                                    break
                                codes.add(code)

# Basisverzeichnis und Cache-Pfad
base_directory = '.'  # Setzen Sie hier Ihren Basispfad
cache_path = '../snippet_cache.db'  # Pfad zur Cache-Datei
find_failed_after_success(base_directory)
find_problematic_responses(base_directory, cache_path)

