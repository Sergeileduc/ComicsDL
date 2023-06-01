"""Some functions with urls."""

import requests
from requests.exceptions import HTTPError

user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'  # noqa: E501
headers = {'User-Agent': user_agent}


def getfinalurl(url):
    """Follow redirections and get final url."""
    try:
        response = requests.get(url, headers=headers)
        if response.history:
            print("Request was redirected")
            # for resp in response.history:
            #     print(resp.status_code, resp.url)
            return response.url
        else:
            return url
    except HTTPError:
        print("down_com got HTTPError")
        return url
