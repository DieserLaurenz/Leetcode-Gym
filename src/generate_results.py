import os
import json
import pandas as pd
from collections import defaultdict

def generate_results(response_directory, save_directory, difficulty_order=None):
    data = []
    if difficulty_order is None:
        difficulty_order = ["Easy", "Medium", "Hard"]

    for difficulty in difficulty_order:
        difficulty_path = os.path.join(response_directory, difficulty)
        if not os.path.exists(difficulty_path):
            continue

        for root, dirs, files in os.walk(difficulty_path):
            problem_info_file = [f for f in files if f.endswith('.json') and not f.startswith("response")]
            problem_name, acRate, topics = None, None, []
            if problem_info_file:
                problem_info_path = os.path.join(root, problem_info_file[0])
                with open(problem_info_path, 'r') as f:
                    problem_info = json.load(f)
                    problem_name = problem_info_file[0].replace('.json', '')
                    acRate = problem_info.get("acRate", None)
                    topicTags = problem_info.get("topicTags", [])
                    topics = [tag["name"] for tag in topicTags]

            for name in dirs:
                if name == 'responses':
                    response_dir_path = os.path.join(root, name)
                    for language_dir in os.listdir(response_dir_path):
                        language_path = os.path.join(response_dir_path, language_dir)
                        attempts_info = {
                            "Problem Name": problem_name,
                            "AC Rate": acRate,
                            "Language": language_dir,
                            "Difficulty": difficulty,
                            "Topics": topics,
                            "Solved": False,
                            "Attempt": None,
                            "Error Messages": {},  # Änderung zu einem Dictionary
                            "Status Runtime": None,
                            "Memory MB": None,
                            "Runtime Percentile": None,
                            "Memory Percentile": None
                        }

                        for file in sorted(os.listdir(language_path)):
                            if file.startswith("response") and file.endswith(".json"):
                                with open(os.path.join(language_path, file), 'r') as f:
                                    content = json.load(f)
                                    attempt_match = file.split('_')
                                    if "success" in file:
                                        attempts_info["Solved"] = True
                                        attempts_info["Attempt"] = attempt_match[2]
                                        attempts_info["Status Runtime"] = content.get("status_runtime")
                                        attempts_info["Memory MB"] = content.get("memory") / 1000000
                                        attempts_info["Runtime Percentile"] = content.get("runtime_percentile")
                                        attempts_info["Memory Percentile"] = content.get("memory_percentile")
                                        break
                                    else:
                                        status_msg = content.get("status_msg", "No error message provided")
                                        # Speichert die Fehlermeldung als Key-Value-Paar
                                        attempts_info["Error Messages"][f"{attempt_match[2]}"] = status_msg
                        
                        data.append(attempts_info)

    df = pd.DataFrame(data)

    df.to_csv(f"{save_directory}/main_results.csv", index=False)
    df.to_pickle(f"{save_directory}/main_results.pkl")
    return df

save_directory = "../results/"
response_directory = "../questions/"

# Beispiel: Rufe die Funktion auf und sortiere die Ergebnisse dynamisch nach Schwierigkeitsgrad
df_detailed_success_info = generate_results(response_directory, save_directory, difficulty_order=["Easy", "Medium", "Hard"])

print(df_detailed_success_info)

