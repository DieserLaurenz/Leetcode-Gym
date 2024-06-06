import json
import os
import pandas as pd

def generate_error_report(questions_directory, output_file):
    print("Generating error report...")
    error_data = []

    for root, dirs, files in os.walk(questions_directory):
        for file in files:
            if file.endswith('.json'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    print(f"Processing file: {file_path}")  # Zeigt die aktuell verarbeitete Datei an
                    language = data.get("lang")  # Sprache aus der Spalte 'lang' lesen
                    compile_error = data.get("full_compile_error")
                    code = data.get("code")

                    if not compile_error and data.get("status_msg") == "Compile Error":
                        compile_error = data.get("compile_error")

                    runtime_error = data.get("full_runtime_error")

                    if not runtime_error and data.get("status_msg") == "Runtime Error":
                        runtime_error = data.get("runtime_error")

                    # Speichern der Fehlermeldungen für Compile-Fehler
                    if compile_error:
                        error_data.append({
                            "Language": language,
                            "Error Type": "compile_error",
                            "Message": compile_error,
                            "File Path": file_path,
                            "Code": code 
                        })
                    
                    # Speichern der Fehlermeldungen für Runtime-Fehler
                    if runtime_error:
                        error_data.append({
                            "Language": language,
                            "Error Type": "runtime_error",
                            "Message": runtime_error,
                            "File Path": file_path,
                            "Code": code 
                        })

    """
                    if data.get("status_msg") == "Memory Limit Exceeded":
                        error_data.append({
                            "Language": language,
                            "Error Type": "memory_limit_exceeded_error",
                            "Message": compile_error,
                            "File Path": file_path
                        })

                    if data.get("status_msg") == "Time Limit Exceeded":
                        error_data.append({
                            "Language": language,
                            "Error Type": "time_limit_exceeded_error",
                            "Message": compile_error,
                            "File Path": file_path
                        })
    """
    # Erstellen einer DataFrame aus den gesammelten Daten
    df = pd.DataFrame(error_data)
    # Sortieren der Daten nach Sprache und Fehlertyp
    df.sort_values(by=["Language", "Error Type"], inplace=True)
    # Speichern der Daten in einer CSV-Datei
    df.to_csv(output_file, index=False)

    print("Error report generated.")

if __name__ == "__main__":
    questions_directory = "../questions/"
    output_file = "../results/errors_report.csv"
    generate_error_report(questions_directory, output_file)
