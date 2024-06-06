import matplotlib
import pandas as pd
import os
import locale

matplotlib.use('Agg')  # Or 'TkAgg', 'Qt5Agg', etc., based on your environment
import matplotlib.pyplot as plt

# Setze Arial als Standard-Schriftart
#matplotlib.rcParams['font.family'] = 'Arial'

# Lokale Einstellungen auf Deutsch setzen, um Kommas als Dezimalzeichen zu verwenden
locale.setlocale(locale.LC_NUMERIC, 'de_DE')


def create_solved_and_total_problems_ranking(df):
    # Base counts
    solved_counts = df[df["Solved"] == True].groupby("Language").size().reset_index(name='Solved Problems')
    total_counts = df.groupby("Language").size().reset_index(name='Total Problems')
    ranking = pd.merge(total_counts, solved_counts, on="Language", how="left")

    # Difficulty level counts
    for difficulty in ['Easy', 'Medium', 'Hard']:
        solved_difficulty = df[(df["Solved"] == True) & (df["Difficulty"] == difficulty)].groupby(
            "Language").size().reset_index(name=f'Solved {difficulty}')
        total_difficulty = df[df["Difficulty"] == difficulty].groupby("Language").size().reset_index(
            name=f'Total {difficulty}')

        # Merge solved and total counts for each difficulty level into the ranking DataFrame
        ranking = pd.merge(ranking, total_difficulty, on="Language", how="left")
        ranking = pd.merge(ranking, solved_difficulty, on="Language", how="left")

    # Replace NaN values with 0
    for column in ranking.columns:
        if 'Solved' in column or 'Total' in column:  # Applies to both overall and difficulty-specific columns
            ranking[column] = ranking[column].fillna(0)

    # Sort results: primary by total solved problems, secondary by total problems
    ranking = ranking.sort_values(by=['Solved Problems', 'Total Problems'], ascending=[False, True]).reset_index(
        drop=True)

    return ranking


def count_errors(df):
    error_df = pd.DataFrame(columns=['Language', 'Error Type', 'Count'])

    for _, row in df.iterrows():
        language = row['Language']
        error_messages = row['Error Messages']

        for message in error_messages.values():
            if error_df[(error_df['Language'] == language) & (error_df['Error Type'] == message)].empty:
                new_row = pd.DataFrame({'Language': [language], 'Error Type': [message], 'Count': [1]})
                error_df = pd.concat([error_df, new_row], ignore_index=True)
            else:
                error_df.loc[(error_df['Language'] == language) & (error_df['Error Type'] == message), 'Count'] += 1

    unique_languages = error_df['Language'].unique()
    required_errors = ["Wrong Answer", "Time Limit Exceeded", "Runtime Error", "Compile Error", "Memory Limit Exceeded"]

    for language in unique_languages:
        for error_type in required_errors:
            if error_df[(error_df['Language'] == language) & (error_df['Error Type'] == error_type)].empty:
                new_row = pd.DataFrame({'Language': [language], 'Error Type': [error_type], 'Count': [0]})
                error_df = pd.concat([error_df, new_row], ignore_index=True)

    error_df = error_df.sort_values(by=['Language', 'Error Type'])

    return error_df


def save_count_error_plot(df, difficulty_path):
    # Daten in Prozent umrechnen
    df_pivot = df.pivot(index='Language', columns='Error Type', values='Count').fillna(0)
    df_percent = df_pivot.div(df_pivot.sum(axis=1), axis=0) * 100

    # Optional: Sortierung nach Gesamtzahl der Fehler, falls gewünscht
    df_percent = df_percent.sort_values(by=df_percent.columns.tolist()).fillna(0)

    # Erstellung eines gestapelten Balkendiagramms
    ax = df_percent.plot(kind='bar', stacked=True, figsize=(10, 7), colormap='viridis')

    # Titel entfernen und Achsenbeschriftungen auf Deutsch übersetzen
    plt.xlabel('Programmiersprache', fontsize=12)
    plt.ylabel('Anteil der Fehlertypen (%)', fontsize=12)

    plt.xticks(rotation=45)

    # Umkehrung der Reihenfolge der Legende
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles[::-1], labels[::-1], title='Fehlertyp', loc='upper right', bbox_to_anchor=(1, 1))

    plt.tight_layout()

    # Speichern des Plots mit minimalem Rand
    plt.savefig(f'{difficulty_path}/error_analysis_chart.png', bbox_inches='tight', pad_inches=0.1)
    plt.close()


def mean_runtime_percentiles(df):
    grouped_language = df.groupby('Language')
    runtime_averages = grouped_language[['Runtime Percentile']].mean()
    sorted_runtime_averages = runtime_averages.sort_values(by=['Runtime Percentile'], ascending=False)
    return sorted_runtime_averages


def mean_memory_percentiles(df):
    grouped_language = df.groupby('Language')
    memory_averages = grouped_language[['Memory Percentile']].mean()
    sorted_memory_averages = memory_averages.sort_values(by=['Memory Percentile'], ascending=False)
    return sorted_memory_averages

def percentage_success_attempts(df):
    # Schritt 1: Filtere gelöste Probleme
    solved_df = df[df['Solved'] == True]

    # Schritt 2: Berechne die Gesamtzahl der Lösungen pro Sprache und die Anzahl der Lösungen pro Versuch
    total_solutions_per_language = solved_df.groupby('Language').size()
    solutions_per_attempt = solved_df.groupby(['Language', 'Attempt']).size()

    # Schritt 3: Berechne Prozentwerte
    percentage_solutions = solutions_per_attempt.unstack(fill_value=0).div(total_solutions_per_language, axis=0) * 100

    return percentage_solutions

def save_count_success_attempt(df, difficulty_folder_path):

    # Sortieren des DataFrames nach 'Versuch 0'
    df = df.sort_values(by='0', ascending=True)

    df.plot(kind='bar', stacked=True, figsize=(10, 6))
    plt.title('Prozentualer Anteil der Lösungen nach Versuch und Sprache')
    plt.xlabel('Sprache')
    plt.ylabel('Prozentualer Anteil der Lösungen')
    plt.xticks(rotation=45)
    plt.legend(title='Versuch', labels=['Versuch 0', 'Versuch 1', 'Versuch 2'])
    plt.tight_layout()

    # Füge eine Beschriftung hinzu, um die Prozentsätze anzuzeigen
    for n, x in enumerate([*df.index.values]):
        for (prozent, y) in zip([*df.loc[x]], df.loc[x].cumsum()):
            plt.text(n, y - (prozent / 2), f'{prozent:.1f}%', ha='center', va='center', color='white', rotation=90)

    plt.savefig(f'{difficulty_folder_path}/count_success_attempt.png')



def save_solved_plot(data, filename_prefix):
    categories = {
        'Einfach': ('Total Easy', 'Solved Easy'),
        'Mittelschwer': ('Total Medium', 'Solved Medium'),
        'Schwer': ('Total Hard', 'Solved Hard')
    }

    german_labels = {
        'Einfach': 'einfache',
        'Mittelschwer': 'mittelschwere',
        'Schwer': 'schwere'
    }
    
    paths = {
        'Einfach': 'Easy',
        'Mittelschwer': 'Medium',
        'Schwer': 'Hard'
    }
    
    bar_color = 'darkgrey'
    
    for difficulty, (total_col, solved_col) in categories.items():
        data[f'Solved {difficulty} Percentage'] = (data[solved_col] / data[total_col]) * 100
        sorted_data = data.sort_values(by=f'Solved {difficulty} Percentage', ascending=False)
        
        plt.figure(figsize=(12, 8))
        bars = plt.bar(sorted_data['Language'], sorted_data[f'Solved {difficulty} Percentage'], color=bar_color)
        plt.ylabel(f'Gelöste {german_labels[difficulty]} Probleme (%)', fontsize=12)
        plt.xlabel('Programmiersprache', fontsize=12)
        plt.xticks(rotation=45, ha='right')
        plt.ylim(0, 100)
        plt.grid(False)
        
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2, height + 0.5, f'{height:.2f}'.replace('.', ','), 
                     va='bottom', ha='center', fontsize=10, color='black')
        
        plt.savefig(f'../results/{paths[difficulty]}/{filename_prefix}_{difficulty.lower()}.png', bbox_inches='tight', pad_inches=0.1)
        plt.close()

    data['Solved Percentage'] = (data['Solved Problems'] / data['Total Problems']) * 100
    
    plt.figure(figsize=(12, 8))
    bars = plt.bar(data['Language'], data['Solved Percentage'], color=bar_color)
    plt.ylabel('Gelöste Probleme (%)', fontsize=12)
    plt.xlabel('Programmiersprache', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.ylim(0, 100)
    plt.grid(False)
    
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, height + 0.5, f'{height:.2f}'.replace('.', ','), 
                 va='bottom', ha='center', fontsize=10, color='black')
    plt.savefig("../results/Total/" + f"{filename_prefix}_total.png", bbox_inches='tight', pad_inches=0.1)
    plt.close()

def save_runtime_and_memory_plot(runtime_averages, memory_averages):
    
    bar_color = 'darkgrey'
    upper_limit = 102  # Maximum y-axis value
    buffer_space = 5   # Space below the graph edge for text

    plt.figure(figsize=(12, 8))
    bars = plt.bar(runtime_averages.index, runtime_averages['Runtime Percentile'], color=bar_color)
    plt.ylabel('Durchschnittliches Laufzeitperzentil (%)', fontsize=12)
    plt.xlabel('Programmiersprache', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.ylim(0, upper_limit)
    plt.grid(False)

    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, height + 0.5, f'{height:.2f}'.replace('.', ','), 
                 va='bottom', ha='center', fontsize=10, color='black')
    
    plt.savefig("../results/Total/total_runtime_averages.png", bbox_inches='tight', pad_inches=0.1)
    plt.close()

    plt.figure(figsize=(12, 8))
    bars = plt.bar(memory_averages.index, memory_averages['Memory Percentile'], color=bar_color)
    plt.ylabel('Durchschnittliches Speicherperzentil (%)', fontsize=12)
    plt.xlabel('Programmiersprache', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.ylim(0, upper_limit)
    plt.grid(False)

    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, height + 0.5, f'{height:.2f}'.replace('.', ','), 
                 va='bottom', ha='center', fontsize=10, color='black')
    
    plt.savefig("../results/Total/total_memory_averages.png", bbox_inches='tight', pad_inches=0.1)
    plt.close()


def run_analysis():

    file_path = '../results/results.pkl'
    df = pd.read_pickle(file_path)

    ranking_df = create_solved_and_total_problems_ranking(df)
    print(ranking_df)
    ranking_df.to_csv(f"../results/solved_problems_analysis.csv", index=False)

    unique_difficulties = df['Difficulty'].unique()

    for difficulty in unique_difficulties:

        difficulty_folder_path = f"../results/{difficulty}"
        if not os.path.exists(difficulty_folder_path):
            os.makedirs(difficulty_folder_path)
        
        filtered_df = df[df["Difficulty"] == difficulty]

        errors_df = count_errors(filtered_df)
        print(errors_df)
        errors_df.to_csv(f"{difficulty_folder_path}/error_analysis.csv", index=False)
        save_count_error_plot(errors_df, difficulty_folder_path)

        runtime_averages = mean_runtime_percentiles(filtered_df)
        runtime_averages.to_csv(f"{difficulty_folder_path}/runtime_analysis.csv")
        memory_averages = mean_memory_percentiles(filtered_df)
        memory_averages.to_csv(f"{difficulty_folder_path}/memory_analysis.csv")

        #percentage_solutions_df = percentage_success_attempts(filtered_df)
        #print(percentage_solutions_df)
        #save_count_success_attempt(percentage_solutions_df, difficulty_folder_path)


    difficulty_folder_path = f"../results/Total"
    if not os.path.exists(difficulty_folder_path):
        os.makedirs(difficulty_folder_path)

    errors_df = count_errors(df)
    print(errors_df)
    errors_df.to_csv(f"{difficulty_folder_path}/error_analysis.csv", index=False)
    save_count_error_plot(errors_df, difficulty_folder_path)

    runtime_averages = mean_runtime_percentiles(df)
    runtime_averages.to_csv(f"{difficulty_folder_path}/runtime_analysis.csv")
    memory_averages = mean_memory_percentiles(df)
    memory_averages.to_csv(f"{difficulty_folder_path}/memory_analysis.csv")

    percentage_solutions_df = percentage_success_attempts(df)
    print(percentage_solutions_df)
    save_count_success_attempt(percentage_solutions_df, difficulty_folder_path)

    save_solved_plot(ranking_df, 'solved_problems')

    save_runtime_and_memory_plot(runtime_averages, memory_averages)

run_analysis()