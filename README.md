
# LeetCode Scraper und Analysetool

Dieses Projekt ermöglicht es, LeetCode-Probleme zu fetchen und anschließend Datenanalysen durchzuführen.

## Erste Schritte

Um das Projekt zu verwenden, befolgen Sie die untenstehenden Schritte.

### Voraussetzungen

- Python 3.x
- Ein LeetCode-Konto
- Ein OpenAI-Konto mit GPT-Plus Zugriff

### Einrichtung der virtuellen Umgebung

1. Klone das Repository auf deinen lokalen Computer.
2. Erstelle eine virtuelle Umgebung mit dem Befehl:

   ```bash
   python -m venv venv
   ```

3. Aktiviere die virtuelle Umgebung:

   - **Windows:**

     ```bash
     venv\Scripts\activate
     ```

   - **macOS und Linux:**

     ```bash
     source venv/bin/activate
     ```

### Installation der Abhängigkeiten

Installiere die benötigten Python-Pakete mit:

```bash
pip install -r requirements.txt
```

### Konfigurieren der Umgebungsvariablen

1. Kopiere die Datei `.env.example` und benenne die Kopie in `.env` um.
2. Füge deine persönlichen Werte für die folgenden Variablen in der `.env` Datei ein:
   - `CSRF_TOKEN` - Cookie von deinem eingeloggten LeetCode-Konto (`csrftoken`).
   - `LEETCODE_SESSION` - Cookie von deinem eingeloggten LeetCode-Konto (`LEETCODE_SESSION`).
   - `CHATGPT_SESSION_TOKEN` - Cookie von deinem eingeloggten ChatGPT-Konto (`__Secure-next-auth.session-token`).

### Daten Fetchen

1. Wechsle in den `src` Ordner.
2. Führe die Datei `leetcode_question_scraper.py` aus, um LeetCode-Probleme zu fetchen. Du kannst die Konstanten im Skript anpassen, um deine Anforderungen zu erfüllen:
   - `REQUEST_DELAY`
   - `QUESTIONS_TO_FETCH`
   - `FILTER_OUT_PAID_QUESTIONS`
   - `PROBLEM_FETCH_START_DATE`
   - `REMOVE_QUESTIONS_WITH_IMAGE`
   - `LANGUAGES`

### Datenerhebung starten

Führe die Datei `leetcode_gym.py` aus, um den Datenerhebungsprozess zu starten. Nach Abschluss der Datenerhebung werden die Ergebnisse im `results` Ordner als `results.csv` und `results.pkl` für weitere Analysen gespeichert.

### Optionale Schritte

- Führe das Skript `find_problematic_responses.py` aus, um nach Problemen zu suchen, die während des Datenerhebungsprozesses aufgetreten sind.
- Führe `analyse_results.py` aus, um Analysen zu erstellen. Die Ergebnisse werden ebenfalls im `results` Ordner gespeichert.

## Lizenz

Dieses Projekt ist unter der MIT Lizenz lizenziert - siehe die [LICENSE.md](LICENSE.md) Datei für Details.
