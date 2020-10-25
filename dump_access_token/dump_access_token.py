import re
import sys
try:
    import requests
except ModuleNotFoundError:
    raise ModuleNotFoundError("install the requests module lol")


reddit_username = ""
reddit_password = ""


def _get_args():
    try:
        reddit_username_ = sys.argv[1]
    except IndexError:
        reddit_username_ = reddit_username
    try:
        reddit_password_ = sys.argv[2]
    except IndexError:
        reddit_password_ = reddit_password
    return reddit_username_, reddit_password_


def get_token(redditusername, redditpassword):
    headers = {'User-Agent': 'Firefox'}
    data = {
        'op': 'login',
        'user': redditusername,
        'passwd': redditpassword
    }
    response = requests.post('https://www.reddit.com/post/login', headers=headers, data=data, allow_redirects=False)
    redditsession = response.cookies.get("reddit_session")
    chat_r = requests.get("https://www.reddit.com/chat/", headers=headers, cookies={"reddit_session": redditsession})
    sendbird_scoped_token = re.search(b'"accessToken":"(.*?)"', chat_r.content).group(1).decode()
    return sendbird_scoped_token


if __name__ == "__main__":
    sendbird_scoped_token = get_token(*_get_args())
    print(f"sendbird scoped token ->")
    print(sendbird_scoped_token)
