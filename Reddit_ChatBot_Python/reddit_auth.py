import requests
import uuid
from ._utils.consts import MOBILE_USERAGENT, OAUTH_REDDIT, S_REDDIT, WEB_USERAGENT, OAUTH_CLIENT_ID_B64, WWW_REDDIT, ACCOUNTS_REDDIT


class _RedditAuthBase:
    def __init__(self, api_token=None):
        self.api_token = api_token
        self.sb_access_token = None
        self.user_id = None

    def authenticate(self):
        self._get_userid_sb_token()
        return {'sb_access_token': self.sb_access_token, 'user_id': self.user_id}

    def _get_userid_sb_token(self):
        headers = {
            'User-Agent': MOBILE_USERAGENT,
            'Authorization': f'Bearer {self.api_token}'
        }
        sb_token_j = requests.get(f'{S_REDDIT}/api/v1/sendbird/me', headers=headers).json()
        self.sb_access_token = sb_token_j['sb_access_token']
        user_id_j = requests.get(f'{OAUTH_REDDIT}/api/v1/me.json', headers=headers).json()
        self.user_id = 't2_' + user_id_j['id']


class PasswordAuth(_RedditAuthBase):
    def __init__(self, reddit_username: str, reddit_password: str, twofa: str = None):
        super().__init__()
        self.reddit_username = reddit_username
        self.reddit_password = reddit_password
        self.twofa = twofa
        self._client_vendor_uuid = str(uuid.uuid4())
        self._reddit_session = None

    def authenticate(self):
        if not (self._reddit_session is None and self.api_token is None):
            self.refresh_api_token()
        else:
            self._reddit_session = self._do_login()
            if self._reddit_session is None:
                raise Exception("Wrong username or password")
            self.api_token = self._get_api_token(self._reddit_session)

        return super(PasswordAuth, self).authenticate()

    def _get_api_token(self, reddit_session):
        cookies = {'reddit_session': reddit_session}
        headers = {
            'Authorization': f'Basic {OAUTH_CLIENT_ID_B64}',
            'User-Agent': MOBILE_USERAGENT,
            'client-vendor-id': self._client_vendor_uuid,
        }
        data = '{"scopes":["*"]}'
        response = requests.post(f'{ACCOUNTS_REDDIT}/api/access_token', headers=headers, cookies=cookies, data=data).json()
        api_token = response['access_token']
        return api_token

    def refresh_api_token(self):
        assert self._reddit_session is not None
        cookies = {
            'reddit_session': self._reddit_session,
        }
        headers = {
            'User-Agent': WEB_USERAGENT,
            'Authorization': f'Bearer {self.api_token}',
        }
        data = {
            'accessToken': self.api_token,
            'unsafeLoggedOut': 'false',
            'safe': 'true'
        }
        response = requests.post(f'{WWW_REDDIT}/refreshproxy', headers=headers, cookies=cookies, data=data).json()
        self.api_token = response['accessToken']
        return self.api_token

    def _do_login(self):
        headers = {
            'User-Agent': WEB_USERAGENT,
        }
        data = {
            'op': 'login',
            'user': self.reddit_username,
            'passwd': f'{self.reddit_password}:{self.twofa}' if bool(self.twofa) else self.reddit_password,
            'api_type': 'json'
        }
        response = requests.post(f'{WWW_REDDIT}/api/login/{self.reddit_username}', headers=headers, data=data)
        reddit_session = response.cookies.get("reddit_session")
        return reddit_session


class TokenAuth(_RedditAuthBase):
    def __init__(self, token):
        super().__init__(token)
