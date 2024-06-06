import pandas as pd
import os

data = pd.read_csv("errors_report.csv")

# Extract unique languages
languages = data['Language'].unique()

# Create a separate CSV file for each language
output_files = {}
for lang in languages:
    # Filter data for the current language
    lang_data = data[data['Language'] == lang]

    if not os.path.isdir("errors_by_language"):
        os.mkdir("errors_by_language")
    
    # Define the output file path
    output_file_path = f'errors_by_language/{lang}_errors.csv'
    
    # Save the filtered data to CSV
    lang_data.to_csv(output_file_path, index=False)
