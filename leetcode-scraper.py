from bs4 import BeautifulSoup
import os
import tls_client
import json
import time

REQUEST_DELAY = 0

def send_request(url, cookies=None, headers=None, json_data=None):

    session = tls_client.Session(
        client_identifier="chrome112",
        random_tls_extension_order=True
    )

    res = session.post(
        url=url,
        headers=headers,
        cookies=cookies,
        json=json_data
    )

    return res

def fetch_questions():

    headers = {
        'authority': 'leetcode.com',
        'accept': '*/*',
        'accept-language': 'de-DE,de;q=0.9,en-GB;q=0.8,en;q=0.7,en-US;q=0.6,es;q=0.5,it;q=0.4,fr;q=0.3',
        'authorization': '',
        'content-type': 'application/json',
        'dnt': '1',
        'origin': 'https://leetcode.com',
        'referer': 'https://leetcode.com/problemset/?sorting=W3sic29ydE9yZGVyIjoiREVTQ0VORElORyIsIm9yZGVyQnkiOiJGUk9OVEVORF9JRCJ9XQ%3D%3D',
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }

    json_data = {
    'query': '\n    query problemsetQuestionList($categorySlug: String, $limit: Int, $skip: Int, $filters: QuestionListFilterInput) {\n  problemsetQuestionList: questionList(\n    categorySlug: $categorySlug\n    limit: $limit\n    skip: $skip\n    filters: $filters\n  ) {\n    total: totalNum\n    questions: data {\n      acRate\n      difficulty\n      freqBar\n      frontendQuestionId: questionFrontendId\n      isFavor\n      paidOnly: isPaidOnly\n      status\n      title\n      titleSlug\n      topicTags {\n        name\n        id\n        slug\n      }\n      hasSolution\n      hasVideoSolution\n    }\n  }\n}\n    ',
    'variables': {
        'categorySlug': 'all-code-essentials',
        'skip': 0,
        'limit': 500,
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
        'authority': 'leetcode.com',
        'accept': '*/*',
        'accept-language': 'de-DE,de;q=0.9,en-GB;q=0.8,en;q=0.7,en-US;q=0.6,es;q=0.5,it;q=0.4,fr;q=0.3',
        'authorization': '',
        'baggage': 'sentry-environment=production,sentry-release=8c964d1c,sentry-transaction=%2Fproblems%2F%5Bslug%5D%2F%5B%5B...tab%5D%5D,sentry-public_key=2a051f9838e2450fbdd5a77eb62cc83c,sentry-trace_id=36aebb91d00b4c5fa4bf514605792576,sentry-sample_rate=0.03',
        'content-type': 'application/json',
        'dnt': '1',
        'origin': 'https://leetcode.com',
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
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

def fetch_question_definition():
    pass

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

def add_question_content(filtered_questions):

    for question in filtered_questions:
        title = question["titleSlug"]
        question_content = fetch_question_content(title)

        code_snippets = clean_code_snippets(question_content["data"]["question"]["codeSnippets"])
        content = clean_content(question_content["data"]["question"]["content"])

        question["codeSnippets"] = code_snippets
        question["content"] = content

        print(f"SUCCESSFULLY ADDED QUESTION CONTENT FOR: {title}")
        time.sleep(REQUEST_DELAY)

    return filtered_questions

def check_creation_date():
    pass
    # Still TO DO
# USE THIS REQUEST
"""
import requests

cookies = {
    'gr_user_id': 'c20eeae6-f608-463d-8536-9316811c1efa',
    'csrftoken': '3t2BwQ1zt2HWpBuNoZqhNztBMk7LFQ9I8SEgdEXWRNlIuDop2MUTttXRzcLxtFtT',
    '87b5a3c3f1a55520_gr_last_sent_cs1': 'laurenzgilbert',
    '__stripe_mid': '03a47ab3-0f6f-4511-9e28-b1d6a0324f7a6b1996',
    '_gid': 'GA1.2.1226416597.1704723056',
    '87b5a3c3f1a55520_gr_session_id': '8850a70a-b390-47f9-9566-95b18aca60bb',
    '87b5a3c3f1a55520_gr_last_sent_sid_with_cs1': '8850a70a-b390-47f9-9566-95b18aca60bb',
    '87b5a3c3f1a55520_gr_session_id_sent_vst': '8850a70a-b390-47f9-9566-95b18aca60bb',
    'LEETCODE_SESSION': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJfYXV0aF91c2VyX2lkIjoiMTEyODU1MjAiLCJfYXV0aF91c2VyX2JhY2tlbmQiOiJhbGxhdXRoLmFjY291bnQuYXV0aF9iYWNrZW5kcy5BdXRoZW50aWNhdGlvbkJhY2tlbmQiLCJfYXV0aF91c2VyX2hhc2giOiJmOTJlY2UwZjU0YWQ4Y2JkNTJhMjQ2MjE5NDVhMDliY2Q5NzFjNmI4ZDMzZmYxMGUyOTQzMmRkNzVhZjM2YTE3IiwiaWQiOjExMjg1NTIwLCJlbWFpbCI6ImxhdXJlbnpnaWxiZXJ0QGdtYWlsLmNvbSIsInVzZXJuYW1lIjoibGF1cmVuemdpbGJlcnQiLCJ1c2VyX3NsdWciOiJsYXVyZW56Z2lsYmVydCIsImF2YXRhciI6Imh0dHBzOi8vYXNzZXRzLmxlZXRjb2RlLmNvbS91c2Vycy9hdmF0YXJzL2F2YXRhcl8xNjk4NjYzNTcyLnBuZyIsInJlZnJlc2hlZF9hdCI6MTcwNDgwOTUxMywiaXAiOiI1LjE4MC42MS4yMjMiLCJpZGVudGl0eSI6IjljMWNlMjdmMDhiMTY0NzlkMmUxNzc0MzA2MmIyOGVkIiwic2Vzc2lvbl9pZCI6NTI3ODQxMDB9.DIN2gxA7SyCcehkeAub1ZPODKhbCKSbqQHMFB1BzB3g',
    '_dd_s': 'rum=0&expire=1704810415902',
    '__stripe_sid': 'd964d365-6255-4e1e-8354-4e07a86d5185794873',
    '_ga': 'GA1.1.1899578593.1704278487',
    '87b5a3c3f1a55520_gr_cs1': 'laurenzgilbert',
    '_ga_CDRWKZTDEX': 'GS1.1.1704808858.9.1.1704809962.12.0.0',
}

headers = {
    'authority': 'leetcode.com',
    'accept': '*/*',
    'accept-language': 'de-DE,de;q=0.9,en-GB;q=0.8,en;q=0.7,en-US;q=0.6,es;q=0.5,it;q=0.4,fr;q=0.3',
    'authorization': '',
    'baggage': 'sentry-environment=production,sentry-release=8c964d1c,sentry-transaction=%2Fproblems%2F%5Bslug%5D%2F%5B%5B...tab%5D%5D,sentry-public_key=2a051f9838e2450fbdd5a77eb62cc83c,sentry-trace_id=f12a165118ca4b7794d1dd1f22f38d14,sentry-sample_rate=0.03',
    'content-type': 'application/json',
    # 'cookie': 'gr_user_id=c20eeae6-f608-463d-8536-9316811c1efa; csrftoken=3t2BwQ1zt2HWpBuNoZqhNztBMk7LFQ9I8SEgdEXWRNlIuDop2MUTttXRzcLxtFtT; 87b5a3c3f1a55520_gr_last_sent_cs1=laurenzgilbert; __stripe_mid=03a47ab3-0f6f-4511-9e28-b1d6a0324f7a6b1996; _gid=GA1.2.1226416597.1704723056; 87b5a3c3f1a55520_gr_session_id=8850a70a-b390-47f9-9566-95b18aca60bb; 87b5a3c3f1a55520_gr_last_sent_sid_with_cs1=8850a70a-b390-47f9-9566-95b18aca60bb; 87b5a3c3f1a55520_gr_session_id_sent_vst=8850a70a-b390-47f9-9566-95b18aca60bb; LEETCODE_SESSION=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJfYXV0aF91c2VyX2lkIjoiMTEyODU1MjAiLCJfYXV0aF91c2VyX2JhY2tlbmQiOiJhbGxhdXRoLmFjY291bnQuYXV0aF9iYWNrZW5kcy5BdXRoZW50aWNhdGlvbkJhY2tlbmQiLCJfYXV0aF91c2VyX2hhc2giOiJmOTJlY2UwZjU0YWQ4Y2JkNTJhMjQ2MjE5NDVhMDliY2Q5NzFjNmI4ZDMzZmYxMGUyOTQzMmRkNzVhZjM2YTE3IiwiaWQiOjExMjg1NTIwLCJlbWFpbCI6ImxhdXJlbnpnaWxiZXJ0QGdtYWlsLmNvbSIsInVzZXJuYW1lIjoibGF1cmVuemdpbGJlcnQiLCJ1c2VyX3NsdWciOiJsYXVyZW56Z2lsYmVydCIsImF2YXRhciI6Imh0dHBzOi8vYXNzZXRzLmxlZXRjb2RlLmNvbS91c2Vycy9hdmF0YXJzL2F2YXRhcl8xNjk4NjYzNTcyLnBuZyIsInJlZnJlc2hlZF9hdCI6MTcwNDgwOTUxMywiaXAiOiI1LjE4MC42MS4yMjMiLCJpZGVudGl0eSI6IjljMWNlMjdmMDhiMTY0NzlkMmUxNzc0MzA2MmIyOGVkIiwic2Vzc2lvbl9pZCI6NTI3ODQxMDB9.DIN2gxA7SyCcehkeAub1ZPODKhbCKSbqQHMFB1BzB3g; _dd_s=rum=0&expire=1704810415902; __stripe_sid=d964d365-6255-4e1e-8354-4e07a86d5185794873; _ga=GA1.1.1899578593.1704278487; 87b5a3c3f1a55520_gr_cs1=laurenzgilbert; _ga_CDRWKZTDEX=GS1.1.1704808858.9.1.1704809962.12.0.0',
    'dnt': '1',
    'origin': 'https://leetcode.com',
    'random-uuid': 'c24a4174-870a-8b0c-938a-76e4e199e541',
    'referer': 'https://leetcode.com/problems/find-score-of-an-array-after-marking-all-elements/solutions/',
    'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'sentry-trace': 'f12a165118ca4b7794d1dd1f22f38d14-86d56736dce2e18c-0',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'uuuserid': '2fda2e1f9702473b0cd10f8210046556',
    'x-csrftoken': '3t2BwQ1zt2HWpBuNoZqhNztBMk7LFQ9I8SEgdEXWRNlIuDop2MUTttXRzcLxtFtT',
    'x-newrelic-id': 'UAQDVFVRGwIAUVhbAAMFXlQ=',
}

json_data = {
    'query': '\n    query communitySolutions($questionSlug: String!, $skip: Int!, $first: Int!, $query: String, $orderBy: TopicSortingOption, $languageTags: [String!], $topicTags: [String!]) {\n  questionSolutions(\n    filters: {questionSlug: $questionSlug, skip: $skip, first: $first, query: $query, orderBy: $orderBy, languageTags: $languageTags, topicTags: $topicTags}\n  ) {\n    hasDirectResults\n    totalNum\n    solutions {\n      id\n      title\n      commentCount\n      topLevelCommentCount\n      viewCount\n      pinned\n      isFavorite\n      solutionTags {\n        name\n        slug\n      }\n      post {\n        id\n        status\n        voteStatus\n        voteCount\n        creationDate\n        isHidden\n        author {\n          username\n          isActive\n          nameColor\n          activeBadge {\n            displayName\n            icon\n          }\n          profile {\n            userAvatar\n            reputation\n          }\n        }\n      }\n      searchMeta {\n        content\n        contentType\n        commentAuthor {\n          username\n        }\n        replyAuthor {\n          username\n        }\n        highlights\n      }\n    }\n  }\n}\n    ',
    'variables': {
        'query': '',
        'languageTags': [],
        'topicTags': [],
        'questionSlug': 'find-score-of-an-array-after-marking-all-elements',
        'skip': 0,
        'first': 15,
        'orderBy': 'newest_to_oldest',
    },
    'operationName': 'communitySolutions',
}

response = requests.post('https://leetcode.com/graphql/', cookies=cookies, headers=headers, json=json_data)

# Note: json_data will not be serialized by requests
# exactly as it was in the original request.
#data = '{"query":"\\n    query communitySolutions($questionSlug: String!, $skip: Int!, $first: Int!, $query: String, $orderBy: TopicSortingOption, $languageTags: [String!], $topicTags: [String!]) {\\n  questionSolutions(\\n    filters: {questionSlug: $questionSlug, skip: $skip, first: $first, query: $query, orderBy: $orderBy, languageTags: $languageTags, topicTags: $topicTags}\\n  ) {\\n    hasDirectResults\\n    totalNum\\n    solutions {\\n      id\\n      title\\n      commentCount\\n      topLevelCommentCount\\n      viewCount\\n      pinned\\n      isFavorite\\n      solutionTags {\\n        name\\n        slug\\n      }\\n      post {\\n        id\\n        status\\n        voteStatus\\n        voteCount\\n        creationDate\\n        isHidden\\n        author {\\n          username\\n          isActive\\n          nameColor\\n          activeBadge {\\n            displayName\\n            icon\\n          }\\n          profile {\\n            userAvatar\\n            reputation\\n          }\\n        }\\n      }\\n      searchMeta {\\n        content\\n        contentType\\n        commentAuthor {\\n          username\\n        }\\n        replyAuthor {\\n          username\\n        }\\n        highlights\\n      }\\n    }\\n  }\\n}\\n    ","variables":{"query":"","languageTags":[],"topicTags":[],"questionSlug":"find-score-of-an-array-after-marking-all-elements","skip":0,"first":15,"orderBy":"newest_to_oldest"},"operationName":"communitySolutions"}'
#response = requests.post('https://leetcode.com/graphql/', cookies=cookies, headers=headers, data=data)
"""

def filter_questions(questions):
    filtered_questions = [question for question in questions if not
                     question['paidOnly'] and int(question['frontendQuestionId']) >= 2600]

    return filtered_questions

def save_questions_to_folder(questions):

    for question in questions:

        path = f"./questions/{question['difficulty']}/{question['titleSlug']}"

        if not os.path.exists(path):
            os.makedirs(path)

        with open(f"{path}/{question['titleSlug']}.json", "w+") as f:
            json.dump(question, f, indent=4)



if __name__ == '__main__':
    questions = fetch_questions()

    filtered_questions = filter_questions(questions)

    questions_with_content = add_question_content(filtered_questions)

    save_questions_to_folder(questions_with_content)



