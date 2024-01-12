import json
import os
import shelve
import time
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from colorama import Fore

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
            timeout=5
        )
        response.raise_for_status()  # Raises HTTPError for bad responses
        return response

    except Exception as e:
        print(Fore.LIGHTRED_EX + "Error while sending request: ", e)
        exit()
