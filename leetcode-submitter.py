import json
import os
import shelve
import time
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from colorama import Fore

def send_request_with_session(url, session, cookies=None, headers=None, json_data=None):
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
        response = session.post(
            url=url,
            headers=headers,
            cookies=cookies,
            json=json_data,
            timeout=5
        )
        response.raise_for_status()  # Raises HTTPError for bad responses
        return response, session

    except Exception as e:
        print(Fore.LIGHTRED_EX + "Error while sending request: ", e)
        exit()

def submit_question():

    session = requests.session()

    headers = {
        'authority': 'leetcode.com',
        'accept': '*/*',
        'accept-language': 'de-DE,de;q=0.9,en-GB;q=0.8,en;q=0.7,en-US;q=0.6,es;q=0.5,it;q=0.4,fr;q=0.3',
        'content-type': 'application/json',
        # 'cookie': 'gr_user_id=2953c93e-f176-4182-a6a6-c3843c368224; csrftoken=PDVg5S9W320kPmb8ss9L9E69Yz2TgYxsHI6U8MHUBBC3z0yOWnBJ3WLvcRkGBV0g; 87b5a3c3f1a55520_gr_last_sent_cs1=laurenzgilbert; __stripe_mid=61824b51-fe9e-4408-a7d3-a3210ba64770f1263e; _gid=GA1.2.756917770.1705067593; LEETCODE_SESSION=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJfYXV0aF91c2VyX2lkIjoiMTEyODU1MjAiLCJfYXV0aF91c2VyX2JhY2tlbmQiOiJhbGxhdXRoLmFjY291bnQuYXV0aF9iYWNrZW5kcy5BdXRoZW50aWNhdGlvbkJhY2tlbmQiLCJfYXV0aF91c2VyX2hhc2giOiJmOTJlY2UwZjU0YWQ4Y2JkNTJhMjQ2MjE5NDVhMDliY2Q5NzFjNmI4ZDMzZmYxMGUyOTQzMmRkNzVhZjM2YTE3IiwiaWQiOjExMjg1NTIwLCJlbWFpbCI6ImxhdXJlbnpnaWxiZXJ0QGdtYWlsLmNvbSIsInVzZXJuYW1lIjoibGF1cmVuemdpbGJlcnQiLCJ1c2VyX3NsdWciOiJsYXVyZW56Z2lsYmVydCIsImF2YXRhciI6Imh0dHBzOi8vYXNzZXRzLmxlZXRjb2RlLmNvbS91c2Vycy9hdmF0YXJzL2F2YXRhcl8xNjk4NjYzNTcyLnBuZyIsInJlZnJlc2hlZF9hdCI6MTcwNTA2NzU5MCwiaXAiOiIxOTMuMTc1LjIuMTgiLCJpZGVudGl0eSI6IjljMWNlMjdmMDhiMTY0NzlkMmUxNzc0MzA2MmIyOGVkIiwic2Vzc2lvbl9pZCI6NTI2NTA0MzB9.Fx7LZMhpCKyAYXvkaaytddk6edpKVNzo14s6zEzzW_Q; 87b5a3c3f1a55520_gr_session_id=34e6635b-e7f9-4578-928b-87ad847afc41; 87b5a3c3f1a55520_gr_last_sent_sid_with_cs1=34e6635b-e7f9-4578-928b-87ad847afc41; 87b5a3c3f1a55520_gr_session_id_sent_vst=34e6635b-e7f9-4578-928b-87ad847afc41; _dd_s=rum=0&expire=1705149388143; _ga=GA1.1.962837887.1704119107; _ga_CDRWKZTDEX=GS1.1.1705148149.7.1.1705148568.57.0.0; 87b5a3c3f1a55520_gr_cs1=laurenzgilbert',
        'dnt': '1',
        'origin': 'https://leetcode.com',
        'referer': 'https://leetcode.com/problems/check-if-array-is-good/',
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'x-csrftoken': 'PDVg5S9W320kPmb8ss9L9E69Yz2TgYxsHI6U8MHUBBC3z0yOWnBJ3WLvcRkGBV0g',
    }

    json_data = {
        'lang': 'csharp',
        'question_id': '2892',
        'typed_code': 'using System.Collections.Generic;\n\npublic class Solution {\n    public bool IsGood(int[] nums) {\n        int n = 0;\n        foreach (int num in nums) {\n            n = System.Math.Max(n, num);\n        }\n\n        if (nums.Length != n + 1) {\n            return false;\n        }\n\n        Dictionary<int, int> frequency = new Dictionary<int, int>();\n        foreach (int num in nums) {\n            if (!frequency.ContainsKey(num)) {\n                frequency[num] = 0;\n            }\n            frequency[num]++;\n        }\n\n        for (int i = 1; i <= n; i++) {\n            if (!frequency.ContainsKey(i)) {\n                return false;\n            }\n            int expectedFrequency = (i == n) ? 2 : 1;\n            if (frequency[i] != expectedFrequency) {\n                return false;\n            }\n        }\n\n        return true;\n    }\n}\n',
    }

    cookies = {
        'gr_user_id': '2953c93e-f176-4182-a6a6-c3843c368224',
        'csrftoken': 'PDVg5S9W320kPmb8ss9L9E69Yz2TgYxsHI6U8MHUBBC3z0yOWnBJ3WLvcRkGBV0g',
        '87b5a3c3f1a55520_gr_last_sent_cs1': 'laurenzgilbert',
        '__stripe_mid': '61824b51-fe9e-4408-a7d3-a3210ba64770f1263e',
        '_gid': 'GA1.2.756917770.1705067593',
        'LEETCODE_SESSION': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJfYXV0aF91c2VyX2lkIjoiMTEyODU1MjAiLCJfYXV0aF91c2VyX2JhY2tlbmQiOiJhbGxhdXRoLmFjY291bnQuYXV0aF9iYWNrZW5kcy5BdXRoZW50aWNhdGlvbkJhY2tlbmQiLCJfYXV0aF91c2VyX2hhc2giOiJmOTJlY2UwZjU0YWQ4Y2JkNTJhMjQ2MjE5NDVhMDliY2Q5NzFjNmI4ZDMzZmYxMGUyOTQzMmRkNzVhZjM2YTE3IiwiaWQiOjExMjg1NTIwLCJlbWFpbCI6ImxhdXJlbnpnaWxiZXJ0QGdtYWlsLmNvbSIsInVzZXJuYW1lIjoibGF1cmVuemdpbGJlcnQiLCJ1c2VyX3NsdWciOiJsYXVyZW56Z2lsYmVydCIsImF2YXRhciI6Imh0dHBzOi8vYXNzZXRzLmxlZXRjb2RlLmNvbS91c2Vycy9hdmF0YXJzL2F2YXRhcl8xNjk4NjYzNTcyLnBuZyIsInJlZnJlc2hlZF9hdCI6MTcwNTA2NzU5MCwiaXAiOiIxOTMuMTc1LjIuMTgiLCJpZGVudGl0eSI6IjljMWNlMjdmMDhiMTY0NzlkMmUxNzc0MzA2MmIyOGVkIiwic2Vzc2lvbl9pZCI6NTI2NTA0MzB9.Fx7LZMhpCKyAYXvkaaytddk6edpKVNzo14s6zEzzW_Q',
        '87b5a3c3f1a55520_gr_session_id': '34e6635b-e7f9-4578-928b-87ad847afc41',
        '87b5a3c3f1a55520_gr_last_sent_sid_with_cs1': '34e6635b-e7f9-4578-928b-87ad847afc41',
        '87b5a3c3f1a55520_gr_session_id_sent_vst': '34e6635b-e7f9-4578-928b-87ad847afc41',
        '_dd_s': 'rum=0&expire=1705149388143',
        '_ga': 'GA1.1.962837887.1704119107',
        '_ga_CDRWKZTDEX': 'GS1.1.1705148149.7.1.1705148568.57.0.0',
        '87b5a3c3f1a55520_gr_cs1': 'laurenzgilbert',
    }

    print(Fore.LIGHTCYAN_EX + "[REQUEST] Fetching...")

    response = session.post(
        url="https://leetcode.com/problems/check-if-array-is-good/submit/",
        headers=headers,
        cookies=cookies,
        json=json_data,
        timeout=5
    )

    response_data = response.json()
    submission_id = response_data["submission_id"]
    print(submission_id)

    cookies = {
        'csrftoken': 'PDVg5S9W320kPmb8ss9L9E69Yz2TgYxsHI6U8MHUBBC3z0yOWnBJ3WLvcRkGBV0g',
        'LEETCODE_SESSION': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJfYXV0aF91c2VyX2lkIjoiMTEyODU1MjAiLCJfYXV0aF91c2VyX2JhY2tlbmQiOiJhbGxhdXRoLmFjY291bnQuYXV0aF9iYWNrZW5kcy5BdXRoZW50aWNhdGlvbkJhY2tlbmQiLCJfYXV0aF91c2VyX2hhc2giOiJmOTJlY2UwZjU0YWQ4Y2JkNTJhMjQ2MjE5NDVhMDliY2Q5NzFjNmI4ZDMzZmYxMGUyOTQzMmRkNzVhZjM2YTE3IiwiaWQiOjExMjg1NTIwLCJlbWFpbCI6ImxhdXJlbnpnaWxiZXJ0QGdtYWlsLmNvbSIsInVzZXJuYW1lIjoibGF1cmVuemdpbGJlcnQiLCJ1c2VyX3NsdWciOiJsYXVyZW56Z2lsYmVydCIsImF2YXRhciI6Imh0dHBzOi8vYXNzZXRzLmxlZXRjb2RlLmNvbS91c2Vycy9hdmF0YXJzL2F2YXRhcl8xNjk4NjYzNTcyLnBuZyIsInJlZnJlc2hlZF9hdCI6MTcwNTA2NzU5MCwiaXAiOiIxOTMuMTc1LjIuMTgiLCJpZGVudGl0eSI6IjljMWNlMjdmMDhiMTY0NzlkMmUxNzc0MzA2MmIyOGVkIiwic2Vzc2lvbl9pZCI6NTI2NTA0MzB9.Fx7LZMhpCKyAYXvkaaytddk6edpKVNzo14s6zEzzW_Q',
    }

    headers = {
        'referer': 'https://leetcode.com/problems/check-if-array-is-good/',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'x-csrftoken': 'PDVg5S9W320kPmb8ss9L9E69Yz2TgYxsHI6U8MHUBBC3z0yOWnBJ3WLvcRkGBV0g',
    }

    time.sleep(10)

    response = session.get(
        url=f"https://leetcode.com/submissions/detail/{submission_id}/check/",
        headers=headers,
        cookies=cookies,
        timeout=5
    )

    response_data = response.json()
    print(response_data)



submit_question()