import requests
import uuid


class _RedditAuthBase:
    _mobile_useragent = "Reddit/Version 2020.47.0/Build 302202/Android 11"
    REDDIT_OAUTH_HOST = "https://oauth.reddit.com"
    REDDIT_SENDBIRD_HOST = "https://s.reddit.com"

    def __init__(self, _api_token=None):
        self._api_token = _api_token

    def authenticate(self):
        sb_access_token, user_id = self._get_userid_sb_token(self._api_token)
        return {'sb_access_token': sb_access_token, 'user_id': user_id, "api_token": self._api_token}

    def _get_userid_sb_token(self, api_token):
        headers = {
            'User-Agent': self._mobile_useragent,
            'Authorization': f'Bearer {api_token}'
        }
        sb_token_j = requests.get(f'{self.REDDIT_SENDBIRD_HOST}/api/v1/sendbird/me', headers=headers).json()
        sb_access_token = sb_token_j['sb_access_token']
        user_id_j = requests.get(f'{self.REDDIT_OAUTH_HOST}/api/v1/me.json', headers=headers).json()
        user_id = 't2_' + user_id_j['id']
        return sb_access_token, user_id


class PasswordAuth(_RedditAuthBase):
    _web_useragent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0"
    OAUTH_CLIENT_ID_B64 = "b2hYcG9xclpZdWIxa2c6"

    def __init__(self, reddit_username, reddit_password, twofa=None):
        super().__init__()
        self.reddit_username = reddit_username
        self.reddit_password = reddit_password
        self.twofa = twofa
        self._client_vendor_uuid = str(uuid.uuid4())

    def authenticate(self):
        reddit_session = self._do_login()
        if reddit_session is None:
            raise Exception("Wrong username or password")
        self._api_token = self._get_api_token(reddit_session)
        return super(PasswordAuth, self).authenticate()

    def _get_api_token(self, reddit_session):
        cookies = {
            'reddit_session': reddit_session,
        }
        headers = {
            'Authorization': f'Basic {self.OAUTH_CLIENT_ID_B64}',
            'User-Agent': self._mobile_useragent,
            'Content-Type': 'application/json; charset=UTF-8',
            'client-vendor-id': self._client_vendor_uuid,
        }
        data = '{"scopes":["*"]}'
        response = requests.post('https://accounts.reddit.com/api/access_token', headers=headers, cookies=cookies, data=data).json()
        api_token = response['access_token']
        return api_token

    def _do_login(self):
        headers = {
            'User-Agent': self._web_useragent,
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        }
        data = {
            'op': 'login',
            'user': self.reddit_username,
            'passwd': f'{self.reddit_password}:{self.twofa}' if self.twofa is not None else self.reddit_password,
            'api_type': 'json'
        }
        response = requests.post(f'https://old.reddit.com/api/login/{self.reddit_username}', headers=headers, data=data, allow_redirects=False)
        reddit_session = response.cookies.get("reddit_session")
        return reddit_session


class TokenAuth(_RedditAuthBase):
    def __init__(self, token):
        super().__init__(token)
