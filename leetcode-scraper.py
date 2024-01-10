import json
import os
import shelve
import time
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from colorama import Fore

REQUEST_DELAY = 2
QUESTIONS_TO_FETCH = 400  # Ascending problem number
FILTER_OUT_PAID_QUESTIONS = True
PROBLEM_FETCH_START_DATE = "14-05-2023"  # DD-MM-YYYY (UTC+2)


def send_request(url, cookies=None, headers=None, json_data=None):
    try:
        response = requests.post(
            url=url,
            headers=headers,
            cookies=cookies,
            json=json_data,
            timeout=5
        )
        response.raise_for_status()  # Raises HTTPError for bad responses
        return response

    except Exception as e:
        print(Fore.LIGHTRED_EX + "Error while sending request: ", e)
        exit()


def fetch_questions():
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }

    json_data = {
        'query': '\n    query problemsetQuestionList($categorySlug: String, $limit: Int, $skip: Int, $filters: QuestionListFilterInput) {\n  problemsetQuestionList: questionList(\n    categorySlug: $categorySlug\n    limit: $limit\n    skip: $skip\n    filters: $filters\n  ) {\n    total: totalNum\n    questions: data {\n      acRate\n      difficulty\n      freqBar\n      frontendQuestionId: questionFrontendId\n      isFavor\n      paidOnly: isPaidOnly\n      status\n      title\n      titleSlug\n      topicTags {\n        name\n        id\n        slug\n      }\n      hasSolution\n      hasVideoSolution\n    }\n  }\n}\n    ',
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
        print(Fore.LIGHTCYAN_EX + "[REQUEST] Fetching questions...")
        res = send_request("https://leetcode.com/graphql/", headers=headers, json_data=json_data)

        # Check if the HTTP request was successful
        if res.status_code == 200:
            try:
                response_data = res.json()
            except ValueError as e:
                print(Fore.LIGHTRED_EX + "Error decoding JSON:", e)
                exit()

            # Safely extract questions from response_data
            questions = response_data.get("data", {}).get("problemsetQuestionList", {}).get("questions")
            if questions is not None:
                print(Fore.LIGHTGREEN_EX + "Successfully fetched questions!")
                return questions
            else:
                print(Fore.LIGHTRED_EX + "Questions data not found in response")
                exit()
        else:
            print(Fore.LIGHTRED_EX + f"Failed to fetch questions. HTTP Status Code: {res.status_code}")
            exit()

    except Exception as e:
        print(Fore.LIGHTRED_EX + "An error occurred:", e)
        exit()


def fetch_question_content(title):
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

    res = send_request("https://leetcode.com/graphql/", headers=headers, json_data=json_data)

    response_data = res.json()

    return response_data


def clean_content(html_text):
    """
    Cleans the provided content, removing tags, newlines, tab characters,
    unicode characters, and formats the text by correcting quotation marks.
    """

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(html_text, 'html.parser')

    # Get text from the parsed HTML
    text = soup.get_text()

    # Replace newline and tab characters with a space
    text = text.replace('\n', ' ').replace('\t', ' ')

    # Remove unicode characters like \u00a0
    text = str(text.encode('ascii', 'ignore').decode('ascii'))

    return text


def clean_code_snippets(code_snippets):
    for code_snippet in code_snippets:
        code_snippet["code"] = code_snippet["code"].replace('\n', ' ').replace('\t', ' ')

    return code_snippets


def add_question_content_and_save_to_file(filtered_questions):

    for question in filtered_questions:

        path = f"./questions/{question['difficulty']}/{question['titleSlug']}/{question['titleSlug']}.json"

        if os.path.exists(path):
            print(Fore.LIGHTYELLOW_EX + f"File has already been created: {question['titleSlug']}")
            continue

        title = question["titleSlug"]

        print(Fore.LIGHTCYAN_EX + f"[REQUEST] Fetching question content: {title}")

        question_content = fetch_question_content(title)

        print(Fore.LIGHTGREEN_EX + f"Successfully fetched content: {title}")

        print(Fore.LIGHTWHITE_EX + f"Cleaning up content: {title}")
        code_snippets = clean_code_snippets(question_content["data"]["question"]["codeSnippets"])
        content = clean_content(question_content["data"]["question"]["content"])
        print(Fore.LIGHTGREEN_EX + f"Successfully cleaned up content: {title}")

        print(Fore.LIGHTWHITE_EX + f"Adding content: {title}")

        question["codeSnippets"] = code_snippets
        question["content"] = content

        print(Fore.LIGHTGREEN_EX + f"Successfully added content: {title}")

        print(Fore.LIGHTWHITE_EX + f"Saving to: {path}")

        save_question_to_folder(question)
        print(Fore.LIGHTGREEN_EX + f"Successfully saved to: {path}")
        time.sleep(REQUEST_DELAY)


def fetch_first_submission_timestamp(title):
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
        print(Fore.LIGHTCYAN_EX + f"[REQUEST] Retrieving timestamp data: {title}")
        res = send_request('https://leetcode.com/graphql/', headers=headers, json_data=json_data)

        # Check if the HTTP request was successful
        if res.status_code == 200:
            try:
                response_data = res.json()
            except ValueError as e:
                print(Fore.LIGHTRED_EX + "Error decoding JSON:", e)
                exit()

            # Safely extract first submission timestamp from response_data
            first_submission_timestamp = response_data.get("data", {}).get("questionSolutions", {}).get("solutions", [{}])[0].get("post", {}).get("creationDate")
            if first_submission_timestamp:
                print(Fore.LIGHTGREEN_EX + f"Timestamp data has successfully been retrieved: {title}")
                return first_submission_timestamp
            else:
                print(Fore.LIGHTRED_EX + "First submission timestamp not found in response")
                exit()
        else:
            print(Fore.LIGHTRED_EX + f"Failed to fetch first submission timestamp. HTTP Status Code: {res.status_code}")
            exit()

    except Exception as e:
        print(Fore.LIGHTRED_EX + "An error occurred:", e)
        exit()


def filter_questions(questions):
    # Convert start date to Unix timestamp once
    try:
        start_date_unix = int(time.mktime(datetime.strptime(PROBLEM_FETCH_START_DATE, "%d-%m-%Y").timetuple()))
    except Exception as e:
        print(Fore.LIGHTRED_EX + "An error occurred while converting datetime to unix timestamp:", e)
        exit()

    # Filter out paid questions if required
    if FILTER_OUT_PAID_QUESTIONS:
        print(Fore.LIGHTWHITE_EX + "Filtering out paid questions...")
        questions = [question for question in questions if not question['paidOnly']]
        print(Fore.LIGHTGREEN_EX + "Successfully filtered out paid questions!")

    filtered_questions = []

    print(Fore.LIGHTWHITE_EX + "Filtering out questions before cutoff date...")

    with shelve.open('request_cache.db') as cache:
        for question in questions:
            title = question['titleSlug']
            cache_key = title

            # Check if data is already in cache
            if cache_key in cache:

                print(Fore.LIGHTYELLOW_EX + f"Timestamp data has already been retrieved: {title}")
                first_submission_timestamp = cache[cache_key]

            else:
                # Fetch data and update cache
                time.sleep(REQUEST_DELAY)
                first_submission_timestamp = fetch_first_submission_timestamp(title)
                cache[cache_key] = first_submission_timestamp

            # Append to filtered questions if criteria are met
            if first_submission_timestamp >= start_date_unix:
                print(Fore.LIGHTGREEN_EX + f"First submission after cutoff date: {title}")
                filtered_questions.append(question)
            else:
                print(Fore.LIGHTRED_EX + f"First submission created before cutoff date: {title}")

    return filtered_questions


def save_question_to_folder(question):
    path = f"./questions/{question['difficulty']}/{question['titleSlug']}"

    if not os.path.exists(path):
        os.makedirs(path)

    with open(f"{path}/{question['titleSlug']}.json", "w+") as f:
        json.dump(question, f, indent=4)


if __name__ == '__main__':
    questions = fetch_questions()

    filtered_questions = filter_questions(questions)

    add_question_content_and_save_to_file(filtered_questions)
