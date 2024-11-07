[![Static Badge](https://img.shields.io/badge/lang-de-blue?style=flat)](https://github.com/DieserLaurenz/Leetcode-Gym/blob/master/README.de.md)

# Leetcode-Gym

 [![ChatGPT](https://img.shields.io/badge/ChatGPT-74aa9c?logo=openai&logoColor=white)](#) [![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=fff)](#)

## Description

This project was developed as part of the bachelor’s thesis titled “Evaluation of ChatGPT 4's Code Generation Capabilities: A Comparative Analysis in 19 Programming Languages.” The goal of the project is to automate the analysis of ChatGPT 4's code generation capabilities by testing the model on LeetCode problems in 19 different programming languages. The results are then examined comparatively, focusing particularly on solution rates, encountered errors, as well as memory and runtime values of the generated solutions.

## Requirements

- Python 3.x
- pip

## Setup

### Step 1: Clone the Repository

Clone this repository to your local computer.

```bash
git clone https://github.com/DieserLaurenz/Leetcode-Gym.git
cd Leetcode-Gym
```

### Step 2: Create a Virtual Environment

Create a virtual environment to avoid conflicts with other projects or system libraries.

```bash
python -m venv venv
```

Activate the virtual environment.

- Windows:
  ```bash
  venv\\Scripts\\activate
  ```
- macOS/Linux:
  ```bash
  source venv/bin/activate
  ```

### Step 3: Install Dependencies

Install all necessary packages from the `requirements.txt` file.

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

Copy `env.example` and create a new file named `.env`. Add the required values for the environment variables:

- `CSRF_TOKEN`: Cookie from logged-in LeetCode.com account (cookie name: `csrftoken`)
- `LEETCODE_SESSION`: Cookie from logged-in LeetCode.com account (cookie name: `LEETCODE_SESSION`)
- `CHATGPT_SESSION_TOKEN`: Cookie from logged-in Chatgpt.com account (cookie name: `__Secure-next-auth.session-token`)

### Step 5: Run Scripts

#### Scrape LeetCode Questions

Navigate to the `src` folder and run the `leetcode_question_scraper.py` script to fetch LeetCode problems. Adjust the constants in the script as needed:

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

#### Start Data Collection

Next, run the `leetcode_gym.py` script to start the data collection process. The results will be stored in the `results` folder as `results.csv` and `results.pkl` for further analysis.

```bash
python leetcode_gym.py
```

### Step 6: Optional Analyses

- `find_problematic_responses.py`: Looks for issues encountered during the data collection process.
- `analyse_results.py`: Performs analyses and saves the results in the `results` folder.
- `error_results.py`: Generates an error report and saves it in the `results` folder.

## License

[MIT](LICENSE)

## Contributions

If you’d like to contribute to improving this project, your pull requests are welcome. For more extensive changes, please open an issue first to discuss the planned changes.

--- 

Let me know if you need any further modifications or clarifications!
