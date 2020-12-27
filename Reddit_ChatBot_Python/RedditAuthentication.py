import re
import requests
from dataclasses import dataclass


@dataclass(frozen=True)
class TokenAuth:
    token: str

    def authenticate(self):
        return self.token


@dataclass(frozen=True)
class PasswordAuth:
    reddit_username: str
    reddit_password: str
    twofa: str = None

    def authenticate(self):
        headers = {'User-Agent': 'Firefox'}
        data = {"op": "login",
                "user": self.reddit_username,
                "passwd": "%s%s" % (self.reddit_password, ":%s" % self.twofa if self.twofa else "")}
        response = requests.post('https://www.reddit.com/post/login', headers=headers, data=data, allow_redirects=False)
        redditsession = response.cookies.get("reddit_session")
        if redditsession is None:
            raise Exception("Wrong username or password")
        chat_r = requests.get('https://www.reddit.com/chat/', headers=headers, cookies={"reddit_session": redditsession})
        token_r = re.search(b'"accessToken":"(.*?)"', chat_r.content)
        if token_r is None:
            raise Exception("Can't get token because of an unknown reason")
        return token_r.group(1).decode()
