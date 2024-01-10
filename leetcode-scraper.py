import datetime
import json
import os
import shelve
import time

import requests
from bs4 import BeautifulSoup

REQUEST_DELAY = 0
QUESTIONS_TO_FETCH = 400  # Ascending problem number


def send_request(url, cookies=None, headers=None, json_data=None):
    res = requests.post(
        url=url,
        headers=headers,
        cookies=cookies,
        json=json_data
    )

    return res


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

    res = send_request("https://leetcode.com/graphql/", headers=headers, json_data=json_data)

    response_data = res.json()

    questions = response_data["data"]["problemsetQuestionList"]["questions"]

    return questions


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
            print(f"{question['titleSlug']} HAS ALREADY BEEN SAVED")
            continue

        title = question["titleSlug"]
        question_content = fetch_question_content(title)

        code_snippets = clean_code_snippets(question_content["data"]["question"]["codeSnippets"])
        content = clean_content(question_content["data"]["question"]["content"])

        question["codeSnippets"] = code_snippets
        question["content"] = content

        print(f"SUCCESSFULLY ADDED QUESTION CONTENT FOR: {title}")
        save_question_to_folder(question)
        print(f"SUCCESSFULLY SAVED QUESTION TO FOLDER: {title}")
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

    response = send_request('https://leetcode.com/graphql/', headers=headers, json_data=json_data)

    response_data = response.json()

    first_submission_timestamp = response_data['data']['questionSolutions']['solutions'][0]['post']['creationDate']

    return first_submission_timestamp


def filter_questions(questions):
    nonpaid_questions = [question for question in questions if not
    question['paidOnly']]

    # Set the date to 14 days after knowledge cutoff to ensure users had enough time to submit answer UTC+0
    date_time = datetime.datetime(2023, 5, 14, 2, 0)

    # Convert the string to datetime object
    unix_timestamp = int(time.mktime(date_time.timetuple()))

    filtered_questions = []

    for question in nonpaid_questions:

        title = question['titleSlug']

        with shelve.open('request_cache.db') as cache:
            cache_key = title

            if cache_key in cache:

                print("TIMESTAMP ALREADY IN CACHE")

                first_submission_timestamp = cache[cache_key]

                if first_submission_timestamp > unix_timestamp:
                    filtered_questions.append(question)
                    print("APPENDED")

            else:
                first_submission_timestamp = fetch_first_submission_timestamp(title)
                cache[cache_key] = first_submission_timestamp

                if first_submission_timestamp > unix_timestamp:
                    filtered_questions.append(question)
                    print("APPENDED")

                time.sleep(REQUEST_DELAY)

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
