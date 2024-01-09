import os
import re

from openai import OpenAI
from dotenv import dotenv_values

# Laden der Konfiguration aus der .env-Datei
config = dotenv_values(".env")

# Initialisierung des OpenAI-Clients
client = OpenAI(
    api_key=config.get("OPENAI_API_KEY")
)

# Initialisierung der Nachrichtenliste
messages = []
user_input = None

while user_input != 'quit':
    user_input = """Solve the following problem in Elixir. Use the template as a starting point

Template:

defmodule Solution do
  @spec find_column_width(grid :: [[integer]]) :: [integer]
  def find_column_width(grid) do
    
  end
end

Problem:

You are given a 0-indexed m x n integer matrix grid. The width of a column is the maximum length of its integers.

For example, if grid = [[-10], [3], [12]], the width of the only column is 3 since -10 is of length 3.
Return an integer array ans of size n where ans[i] is the width of the ith column.

The length of an integer x with len digits is equal to len if x is non-negative, and len + 1 otherwise.

 

Example 1:

Input: grid = [[1],[22],[333]]
Output: [3]
Explanation: In the 0th column, 333 is of length 3.
Example 2:

Input: grid = [[-15,1,3],[15,7,12],[5,6,-2]]
Output: [3,1,2]
Explanation: 
In the 0th column, only -15 is of length 3.
In the 1st column, all integers are of length 1. 
In the 2nd column, both 12 and -2 are of length 2.
 

Constraints:

m == grid.length
n == grid[i].length
1 <= m, n <= 100 
-109 <= grid[r][c] <= 109"""

    messages.append({'role':'user','content':user_input})

    # Senden an die ChatGPT API unter Verwendung aller bisherigen Nachrichten
    response = client.chat.completions.create(
        messages=messages,
        model="gpt-4",  # Überprüfen Sie den Modellnamen
        temperature=0,
        max_tokens=1024,
        n=1,
        stop=None
    )

    # Antwort erhalten und ausgeben
    answer = response.choices[0].message.content

    pattern = r"```elixir\n([\s\S]*?)\n```"

    match = re.search(pattern, answer)

    if match:
        extracted_code = match.group(1)
        print("Extrahierter Code:\n", extracted_code)
    else:
        print("Kein Code gefunden.")

    # Antwort zur Nachrichtenliste hinzufügen
    messages.append({'role':'assistant','content':answer})
