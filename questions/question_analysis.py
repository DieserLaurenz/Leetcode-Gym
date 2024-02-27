import os
import json
import pandas as pd
from collections import defaultdict

def analyze_attempts_with_detailed_success_info(directory, difficulty_order=None):
    data = []
    if difficulty_order is None:
        difficulty_order = ["Easy", "Medium", "Hard"]

    for difficulty in difficulty_order:
        difficulty_path = os.path.join(directory, difficulty)
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
                                        attempts_info["Memory MB"] = content.get("memory") / 1024 / 1024
                                        attempts_info["Runtime Percentile"] = content.get("runtime_percentile")
                                        attempts_info["Memory Percentile"] = content.get("memory_percentile")
                                        break
                                    else:
                                        status_msg = content.get("status_msg", "No error message provided")
                                        # Speichert die Fehlermeldung als Key-Value-Paar
                                        attempts_info["Error Messages"][f"{attempt_match[2]}"] = status_msg
                        
                        data.append(attempts_info)

    df = pd.DataFrame(data)
    return df

# Pfad zum aktuellen Verzeichnis (oder zum Zielverzeichnis anpassen)
current_directory = os.getcwd()

# Beispiel: Rufe die Funktion auf und sortiere die Ergebnisse dynamisch nach Schwierigkeitsgrad
df_detailed_success_info = analyze_attempts_with_detailed_success_info(current_directory, difficulty_order=["Medium", "Hard", "Easy"])
print(df_detailed_success_info)

df_detailed_success_info.to_csv(f"{current_directory}/results_data.csv", index=False)

def create_solved_and_total_problems_ranking(df):
    # Zähle, wie viele Probleme pro Programmiersprache gelöst wurden
    solved_counts = df[df["Solved"] == True].groupby("Language").size().reset_index(name='Solved Problems')
    
    # Zähle die Gesamtzahl der Probleme pro Programmiersprache
    total_counts = df.groupby("Language").size().reset_index(name='Total Problems')
    
    # Führe die beiden DataFrames zusammen, um eine vollständige Übersicht zu erhalten
    ranking = pd.merge(total_counts, solved_counts, on="Language", how="left")
    
    # Ersetze NaN-Werte mit 0 für den Fall, dass es Programmiersprachen gibt, für die keine Probleme gelöst wurden
    ranking['Solved Problems'] = ranking['Solved Problems'].fillna(0)
    
    # Sortiere die Ergebnisse absteigend nach der Anzahl der gelösten Probleme, dann nach Gesamtzahl
    ranking = ranking.sort_values(by=['Solved Problems', 'Total Problems'], ascending=[False, True]).reset_index(drop=True)
    
    return ranking

def count_errors(df):
    # Initialisieren eines neuen DataFrames für die Fehlermeldungen
    error_df = pd.DataFrame(columns=['Language', 'Error Type', 'Count'])

    # Durchgehen aller Einträge im DataFrame
    for _, row in df.iterrows():
        language = row['Language']
        error_messages = row['Error Messages']
        
        # Zählen der Fehlermeldungen
        for message in error_messages.values():
            # Prüfen, ob der Fehler bereits existiert, und zählen
            if error_df[(error_df['Language'] == language) & (error_df['Error Type'] == message)].empty:
                # Wenn der Fehler noch nicht existiert, füge ihn hinzu
                new_row = pd.DataFrame({'Language': [language], 'Error Type': [message], 'Count': [1]})
                error_df = pd.concat([error_df, new_row], ignore_index=True)
            else:
                # Wenn der Fehler bereits existiert, erhöhe den Zähler
                error_df.loc[(error_df['Language'] == language) & (error_df['Error Type'] == message), 'Count'] += 1
                
    # Sortieren des DataFrames nach der Spalte 'Language'
    error_df = error_df.sort_values(by='Language')
    
    return error_df

# Annahme: df_detailed_success_info ist das DataFrame, das wir zuvor erstellt haben
# Erstelle die Rangliste und zeige sie an
ranking_df = create_solved_and_total_problems_ranking(df_detailed_success_info)
print(ranking_df)
errors_df = count_errors(df_detailed_success_info)
print(errors_df)
errors_df.to_csv(f"{current_directory}/error_results.csv", index=False)
