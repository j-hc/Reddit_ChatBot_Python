import re
import requests


class TokenAuth:
    def __init__(self, token: str):
        self._token = token

    def authenticate(self):
        return self._token


class PasswordAuth:
    def __init__(self, reddit_username: str, reddit_password: str):
        self.reddit_username = reddit_username
        self.reddit_password = reddit_password

    def authenticate(self):
        headers = {'User-Agent': 'Firefox'}
        data = {
            'op': 'login',
            'user': self.reddit_username,
            'passwd': self.reddit_password
        }
        response = requests.post('https://www.reddit.com/post/login', headers=headers, data=data, allow_redirects=False)
        redditsession = response.cookies.get("reddit_session")
        chat_r = requests.get('https://www.reddit.com/chat/', headers=headers, cookies={"reddit_session": redditsession})
        sendbird_scoped_token = re.search(b'"accessToken":"(.*?)"', chat_r.content).group(1).decode()
        return sendbird_scoped_token
