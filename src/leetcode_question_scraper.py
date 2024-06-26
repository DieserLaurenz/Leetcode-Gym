import json
import os
import shelve
import time
from datetime import datetime

import requests
from scripts import question_builder
from bs4 import BeautifulSoup

# Constants for configuration
REQUEST_DELAY = 2  # Delay between requests in seconds
QUESTIONS_TO_FETCH = 30  # Number of questions to fetch in ascending order
FILTER_OUT_PAID_QUESTIONS = True  # Flag to filter out paid questions
PROBLEM_FETCH_START_DATE = "14-05-2023"  # Start date for fetching problems (DD-MM-YYYY)
REMOVE_QUESTIONS_WITH_IMAGE = True
LANGUAGES = ["C++", "Java", "JavaScript"]  # Languages that must be included in the question


def send_request(url, cookies=None, headers=None, json_data=None):
    """
    Send a POST request to the given URL with optional cookies, headers, and JSON data.

    Parameters:
    - url (str): The URL to send the request to.
    - cookies (dict, optional): Cookies to be sent with the request.
    - headers (dict, optional): Headers to be sent with the request.
    - json_data (dict, optional): JSON payload for the request.

    Returns:
    - response: The response object from the request.

    Raises:
    - Prints error message and exits on failure.
    """

    try:
        response = requests.post(
            url=url,
            headers=headers,
            cookies=cookies,
            json=json_data,
            timeout=10
        )
        response.raise_for_status()  # Raises HTTPError for bad responses
        return response

    except Exception as e:
        print("Error while sending request: ", e)
        exit()


def fetch_questions():
    """
    Fetch questions from the Leetcode API using a predefined GraphQL query and headers.

    Returns:
    - list: A list of fetched questions, or None if an error occurs.

    Raises:
    - Prints error message and exits on failure.
    """

    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }

    json_data = {
        'query': '\n    query problemsetQuestionList($categorySlug: String, $limit: Int, $skip: Int, $filters: QuestionListFilterInput) {\n  problemsetQuestionList: questionList(\n    categorySlug: $categorySlug\n    limit: $limit\n    skip: $skip\n    filters: $filters\n  ) {\n    total: totalNum\n    questions: data {\n      acRate\n      difficulty\n      freqBar\n      questionId\n    frontendQuestionId: questionFrontendId\n      isFavor\n      paidOnly: isPaidOnly\n      status\n      title\n      titleSlug\n      topicTags {\n        name\n        id\n        slug\n      }\n      hasSolution\n      hasVideoSolution\n    }\n  }\n}\n    ',
        'variables': {
            'categorySlug': 'all-code-essentials',
            'skip': 0,
            'limit': QUESTIONS_TO_FETCH,
            'filters': {
                'orderBy': 'FRONTEND_ID',
                'sortOrder': 'DESCENDING',
            },
        },
        'operationName': 'problemsetQuestionList'
    }

    try:
        print("[REQUEST] Fetching questions...")
        res = send_request("https://leetcode.com/graphql/", headers=headers, json_data=json_data)

        # Check if the HTTP request was successful
        if res.status_code == 200:
            try:
                response_data = res.json()
            except ValueError as e:
                print("Error decoding JSON:", e)
                exit()

            # Safely extract questions from response_data
            questions = response_data.get("data", {}).get("problemsetQuestionList", {}).get("questions")
            if questions is not None:
                print("Successfully fetched questions!")
                return questions
            else:
                print("Questions data not found in response")
                exit()
        else:
            print(f"Failed to fetch questions. HTTP Status Code: {res.status_code}")
            exit()

    except Exception as e:
        print("An error occurred:", e)
        exit()


def filter_questions(questions):
    """
    Filters a list of questions based on certain criteria, such as date and paid status.

    Parameters:
    - questions (list of dict): A list of question dictionaries to be filtered.

    Returns:
    - filtered_questions: A list of filtered question dictionaries.

    Raises:
    - Prints error message and exits on failure.
    """

    # Convert start date to Unix timestamp once
    try:
        start_date_unix = int(time.mktime(datetime.strptime(PROBLEM_FETCH_START_DATE, "%d-%m-%Y").timetuple()))
    except Exception as e:
        print(f"An error occurred while converting datetime to unix timestamp:", e)
        exit()

    # Filter out paid questions if required
    if FILTER_OUT_PAID_QUESTIONS:
        print("Filtering out paid questions...")
        questions = [question for question in questions if not question['paidOnly']]
        print("Successfully filtered out paid questions!")

    filtered_questions = []

    print("Filtering out questions before cutoff date...")

    try:
        with shelve.open('../cache/request_cache.db') as cache:
            for question in questions:
                title = question['titleSlug']
                cache_key = title

                # Check if data is already in cache
                if cache_key in cache:
                    print(f"Timestamp data has already been retrieved: {title}")
                    first_submission_timestamp = cache[cache_key]
                else:
                    # Fetch data and update cache
                    try:
                        time.sleep(REQUEST_DELAY)
                        first_submission_timestamp = fetch_first_submission_timestamp(title)
                        cache[cache_key] = first_submission_timestamp
                    except Exception as e:
                        print(f"An error occurred while fetching timestamp data for {title}:", e)
                        continue

                # Append to filtered questions if criteria are met
                if first_submission_timestamp >= start_date_unix:
                    print(f"First submission after cutoff date: {title}")
                    filtered_questions.append(question)
                else:
                    print(f"First submission created before cutoff date: {title}")
    except Exception as e:
        print("An error occurred while accessing the cache database:", e)
        exit()

    return filtered_questions


def fetch_first_submission_timestamp(title):
    """
    Fetches the timestamp of the first submission for a given question title from an external API.

    Parameters:
    - title (str): The slug of the question title.

    Returns:
    - first_submission_timestamp: The timestamp of the first submission, if successfully retrieved.

    Raises:
    - Prints error message and exits on failure.
    """

    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }

    json_data = {
        'query': '\n    query communitySolutions($questionSlug: String!, $skip: Int!, $first: Int!, $query: String, $orderBy: TopicSortingOption, $languageTags: [String!], $topicTags: [String!]) {\n  questionSolutions(\n    filters: {questionSlug: $questionSlug, skip: $skip, first: $first, query: $query, orderBy: $orderBy, languageTags: $languageTags, topicTags: $topicTags}\n  ) {\n    hasDirectResults\n    totalNum\n    solutions {\n      id\n      title\n      commentCount\n      topLevelCommentCount\n      viewCount\n      pinned\n      isFavorite\n      solutionTags {\n        name\n        slug\n      }\n      post {\n        id\n        status\n        voteStatus\n        voteCount\n        creationDate\n        isHidden\n        author {\n          username\n          isActive\n          nameColor\n          activeBadge {\n            displayName\n            icon\n          }\n          profile {\n            userAvatar\n            reputation\n          }\n        }\n      }\n      searchMeta {\n        content\n        contentType\n        commentAuthor {\n          username\n        }\n        replyAuthor {\n          username\n        }\n        highlights\n      }\n    }\n  }\n}\n    ',
        'variables': {
            'query': '',
            'languageTags': [],
            'topicTags': [],
            'questionSlug': title,
            'skip': 0,
            'first': 1,
            'orderBy': 'oldest_to_newest',
        },
        'operationName': 'communitySolutions',
    }

    try:
        print(f"[REQUEST] Retrieving timestamp data: {title}")
        res = send_request('https://leetcode.com/graphql/', headers=headers, json_data=json_data)

        # Check if the HTTP request was successful
        if res.status_code == 200:
            try:
                response_data = res.json()
            except ValueError as e:
                print("Error decoding JSON:", e)
                exit()

            # Safely extract first submission timestamp from response_data
            first_submission_timestamp = \
                response_data.get("data", {}).get("questionSolutions", {}).get("solutions", [{}])[0].get("post",
                                                                                                         {}).get(
                    "creationDate")
            if first_submission_timestamp:
                print(f"Timestamp data has successfully been retrieved: {title}")
                return first_submission_timestamp
            else:
                print("First submission timestamp not found in response")
                exit()
        else:
            print(f"Failed to fetch first submission timestamp. HTTP Status Code: {res.status_code}")
            exit()

    except Exception as e:
        print("An error occurred:", e)
        exit()


def fetch_question_content(title):
    """
    Fetch question content from the Leetcode API using a predefined GraphQL query and headers.

    Returns:
    - list: A list of fetched question_content, or None if an error occurs.

    Raises:
    - Prints error message and exits on failure.
    """

    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }

    json_data = {
        "query": "\n    query combinedData($titleSlug: String!) {\n  question(titleSlug: $titleSlug) {\n    content\n    mysqlSchemas\n    dataSchemas\n    questionId\n    questionFrontendId\n    codeSnippets {\n      lang\n      langSlug\n      code\n    }\n    envInfo\n    enableRunCode\n    hasFrontendPreview\n    frontendPreviews\n  }\n}\n    ",
        "variables": {
            "titleSlug": title
        },
        "operationName": "combinedData"
    }

    try:
        res = send_request("https://leetcode.com/graphql/", headers=headers, json_data=json_data)

        # Check if the HTTP request was successful
        if res.status_code == 200:
            try:
                response_data = res.json()
            except ValueError as e:
                print("Error decoding JSON:", e)
                exit()

            return response_data
        else:
            print(f"Failed to fetch question content. HTTP Status Code: {res.status_code}")
            exit()

    except Exception as e:
        print("An error occurred:", e)
        exit()


def clean_content(html_text):
    """
    Cleans the provided content by removing tags, unicode characters, and formats the text by correcting quotation marks.

    Parameters:
    - html_text: The HTML content to be cleaned

    Returns:
    - cleaned_text: The cleaned text.

    Raises:
    - Prints error message and exits on failure.
    """

    try:
        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(html_text, 'html.parser')

        # Get text from the parsed HTML
        text = soup.get_text()

        # Replace newline and tab characters with a space
        # cleaned_text = text.replace('\n', ' ').replace('\t', ' ')

        # Remove unicode characters like \u00a0
        cleaned_text = str(text.encode('ascii', 'ignore').decode('ascii'))

    except Exception as e:
        print(f"An error occurred: {e}")
        exit()

    return cleaned_text


def clean_code_snippets(code_snippets):
    """
    Cleans the provided code snippets by removing newlines and tab characters

    Parameters:
    - html_text: The HTML content to be cleaned

    Returns:
    - cleaned_text: The cleaned text.

    Raises:
    - Prints error message and exits on failure.
    """

    cleaned_snippets = []

    for code_snippet in code_snippets:
        try:
            cleaned_code = code_snippet["code"].replace('\n', ' ').replace('\t', ' ')
            cleaned_snippets.append({code_snippet["langSlug"]: cleaned_code})

        except KeyError:
            print("KeyError: 'code' key not found in one of the snippets.")
            continue
        except TypeError:
            print("TypeError: Invalid type encountered in code snippets.")
            continue
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            exit()

    return cleaned_snippets


def check_content_for_image(content):
    try:
        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(content, 'html.parser')

        if soup.find('img'):
            return True
        else:
            return False


    except Exception as e:
        print(f"An error occurred: {e}")
        exit()


def add_question_content_and_save_to_file(filtered_questions):
    """
    Iterate over a list of filtered questions, fetch their content, clean it, and save it to a specific directory.

    Parameters:
    - filtered_questions (list of dict): A list of question dictionaries to process.

    Returns:
    None: The function is used for its side effects (file creation and logging) and does not return a value.
    """

    for question in filtered_questions:

        title = question["titleSlug"]

        path = f"../questions/{question['difficulty']}/{question['titleSlug']}/{question['titleSlug']}.json"

        try:
            if os.path.exists(path):
                print(f"File has already been created: {question['titleSlug']}")
                continue

            print(f"[REQUEST] Fetching question content: {title}")

            try:
                question_content = fetch_question_content(title)
            except Exception as e:
                print(f"Error fetching question content for {title}:", e)
                continue

            print(f"Successfully fetched content: {title}")

            if REMOVE_QUESTIONS_WITH_IMAGE:
                if check_content_for_image(question_content["data"]["question"]["content"]):
                    print(f"Image found in {title}")
                    continue

            try:
                code_snippets = question_content["data"]["question"]["codeSnippets"]
                content = clean_content(question_content["data"]["question"]["content"])
            except Exception as e:
                print(f"Error cleaning content for {title}:", e)
                continue

            available_languages_for_question = [code_snippet["lang"] for code_snippet in code_snippets]

            is_languages_available = all(language in available_languages_for_question for language in LANGUAGES)

            if not is_languages_available:
                print(f"Not all languages available for {title}")
                continue

            question["codeSnippets"] = code_snippets
            question["content"] = content

            try:
                print(f"Saving to: {path}")
                os.makedirs(os.path.dirname(path), exist_ok=True)  # Ensure the directory exists
                save_question_to_folder(question)
            except Exception as e:
                print(f"Error saving {title} to file:", e)
                continue

            print(f"Successfully saved to: {path}")
            time.sleep(REQUEST_DELAY)
        except Exception as e:
            print(f"An unexpected error occurred for {title}:", e)


def save_question_to_folder(question):
    """
    Saves a question dictionary as a JSON file in a specified directory structure.

    Parameters:
    - question (dict): The question dictionary containing the data to be saved.

    Returns:
    None: The function is used for its side effects (file creation) and does not return a value.

    Raises:
    - Prints error message and exits on failure.
    """

    try:
        # Constructing the file path
        path = f"../questions/{question['difficulty']}/{question['titleSlug']}"

        # Creating the directory if it doesn't exist
        if not os.path.exists(path):
            os.makedirs(path)

        # Writing the question data to a JSON file
        with open(f"{path}/{question['titleSlug']}.json", "w+") as f:
            json.dump(question, f, indent=4)

    except KeyError as e:
        print(f"KeyError: Missing key in question dictionary - {e}")
        exit()

    except OSError as e:
        print(f"OSError: Issue with file system operations - {e}")
        exit()

    except json.JSONDecodeError as e:
        print(f"JSONDecodeError: Issue with JSON data - {e}")
        exit()

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        exit()


if __name__ == '__main__':
    questions = fetch_questions()

    filtered_questions = filter_questions(questions)

    add_question_content_and_save_to_file(filtered_questions)

    question_builder.add_prompts_and_url_shortcut()
