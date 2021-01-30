import requests
from .Utils.CONST import SB_PROXY_CHATMEDIA, S_REDDIT, user_agent, SB_User_Agent, SB_ai


class Tools:
    def __init__(self, reddit_auth):
        self.headers = {
            'User-Agent': user_agent,
            'Accept': 'application/json, text/plain, */*',
            'SendBird': f'Android,29,3.0.82,{SB_ai}',
            'SB-User-Agent': SB_User_Agent
        }
        self._reddit_auth = reddit_auth
        try:
            r = self._reddit_auth.reddit_username
            self._is_reauthable = True
        except AttributeError:
            self._is_reauthable = False

    def _handled_req(self, method, uri, **kwargs):
        while True:
            response = requests.request(method, uri, **kwargs)
            if response.status_code == 401 and self._is_reauthable:
                new_access_token = self._reddit_auth.refresh_api_token()
                new_headers = kwargs.get('headers', {})
                new_headers.update({'Authorization': f'Bearer {new_access_token}'})
                kwargs.update({'headers': new_headers})
                continue
            else:
                return response

    def delete_message(self, channel_url, msg_id, session_key):
        headers = {'Session-Key': session_key, **self.headers}
        uri = f"{SB_PROXY_CHATMEDIA}/v3/group_channels/{channel_url}/messages/{msg_id}"
        self._handled_req(method='DELETE', uri=uri, headers=headers)

    def kick_user(self, channel_url, user_id, duration):
        headers = {'Authorization': f'Bearer {self._reddit_auth._api_token}', **self.headers}
        data = f'{{"channel_url":"{channel_url}","user_id":"{user_id}","duration":"{duration}"}}'
        uri = f'{S_REDDIT}/api/v1/channel/kick/user'
        self._handled_req(method='POST', uri=uri, headers=headers, data=data)
