import os
import json
import pandas as pd
from collections import defaultdict
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Or 'TkAgg', 'Qt5Agg', etc., based on your environment
import matplotlib.pyplot as plt
import seaborn as sns


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

def show_count_error_plot(df):
    # Step 2: Manipulate DataFrame for plotting
    df_pivot = df.pivot(index='Language', columns='Error Type', values='Count').fillna(0)

    # Optional: sort by the total count if you prefer
    df_pivot = df_pivot.sort_values(by=df_pivot.columns.tolist()).fillna(0)

    # Step 3: Create a stacked bar chart
    df_pivot.plot(kind='bar', stacked=True, figsize=(10, 7))

    plt.title('Programming Errors by Language')
    plt.xlabel('Programming Language')
    plt.ylabel('Count of Errors')
    plt.xticks(rotation=45)
    plt.legend(title='Error Type')

    plt.tight_layout()

    # Save the plot to a file
    plt.savefig('error_analysis_chart.png')

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


file_path = '../results/main_results.pkl'
df = pd.read_pickle(file_path)

ranking_df = create_solved_and_total_problems_ranking(df)
print(ranking_df)
ranking_df.to_csv("../results/solved_problems_analysis.csv", index=False)
errors_df = count_errors(df)
print(errors_df)
errors_df.to_csv("../results/error_analysis.csv", index=False)
show_count_error_plot(errors_df)

runtime_averages = mean_runtime_percentiles(df)
runtime_averages.to_csv("../results/runtime_analysis.csv")
memory_averages = mean_memory_percentiles(df)
memory_averages.to_csv("../results/memory_analysis.csv")
