
# Leetcode-Gym

## Beschreibung

Dieses Projekt wurde im Rahmen der Bachelorarbeit mit dem Titel "Evaluierung der Code-Generierungsfähigkeiten von ChatGPT 4: Eine vergleichende Analyse in 19 Programmiersprachen" entwickelt. Ziel des Projekts ist die Automatisierung der Analyse der Code-Generierungsfähigkeiten von ChatGPT 4, indem das Modell auf LeetCode-Probleme in 19 verschiedenen Programmiersprachen getestet wird. Im Anschluss werden die Ergebnisse vergleichend untersucht. Dabei werden insbesondere die Lösungsraten, die aufgetretenen Fehler sowie die Speicher- und Laufzeitwerte der generierten Lösungen analysiert.

## Voraussetzungen

- Python 3.x
- pip

## Einrichtung

### Schritt 1: Klonen des Repositories

Klonen Sie dieses Repository auf Ihren lokalen Computer.

```bash
git clone https://github.com/DieserLaurenz/Leetcode-Gym.git
cd Leetcode-Gym
```

### Schritt 2: Erstellen einer virtuellen Umgebung

Erstellen Sie eine virtuelle Umgebung, um Konflikte mit anderen Projekten oder Systembibliotheken zu vermeiden.

```bash
python -m venv venv
```

Aktivieren Sie die virtuelle Umgebung.

- Windows:
  ```bash
  venv\Scripts\activate
  ```
- macOS/Linux:
  ```bash
  source venv/bin/activate
  ```

### Schritt 3: Installieren der Abhängigkeiten

Installieren Sie alle erforderlichen Pakete aus der `requirements.txt` Datei.

```bash
pip install -r requirements.txt
```

### Schritt 4: Konfigurieren der Umgebungsvariablen

Kopieren Sie `env.example` und erstellen Sie eine neue Datei namens `.env`. Fügen Sie die erforderlichen Werte für die Umgebungsvariablen hinzu:

- `CSRF_TOKEN`: Cookie von eingeloggtem LeetCode.com Account (cookie name: `csrftoken`)
- `LEETCODE_SESSION`: Cookie von eingeloggtem LeetCode.com Account (cookie name: `LEETCODE_SESSION`)
- `CHATGPT_SESSION_TOKEN`: Cookie von eingeloggtem Chatgpt.com Account (cookie name: `__Secure-next-auth.session-token`)

### Schritt 5: Ausführen der Skripte

#### LeetCode Fragen schürfen

Navigieren Sie zum `src` Ordner und führen Sie das `leetcode_question_scraper.py` Skript aus, um LeetCode-Probleme zu fetchen. Passen Sie die Konstanten im Skript nach Bedarf an:

- `REQUEST_DELAY`
- `QUESTIONS_TO_FETCH`
- `FILTER_OUT_PAID_QUESTIONS`
- `PROBLEM_FETCH_START_DATE`
- `REMOVE_QUESTIONS_WITH_IMAGE`
- `LANGUAGES`

```bash
cd src
python leetcode_question_scraper.py
```

#### Datenerhebung starten

Führen Sie anschließend das `leetcode_gym.py` Skript aus, um den Datenerhebungsprozess zu starten. Die Ergebnisse werden im `results` Ordner als `results.csv` und `results.pkl` für weitere Analysen gespeichert.

```bash
python leetcode_gym.py
```

### Schritt 6: Optionale Analysen

- `find_problematic_responses.py`: Sucht nach Problemen, die während des Datenerhebungsprozesses aufgetreten sind.
- `analyse_results.py`: Führt Analysen durch und speichert die Ergebnisse im `results` Ordner.
- `error_results.py`: Generiert einen Error-Report und speichert diesen im `results` Ordner.

## Lizenz

[MIT](LICENSE)

## Beiträge

Falls Sie zur Verbesserung dieses Projekts beitragen möchten, sind Ihre Pull-Anfragen willkommen. Für umfangreichere Änderungen eröffnen Sie bitte zunächst ein Issue, um die geplanten Änderungen zu diskutieren.

