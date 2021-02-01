import requests
from .Utils.CONST import SB_PROXY_CHATMEDIA, S_REDDIT, user_agent, SB_User_Agent, SB_ai, web_useragent
import json


def _get_user_id(username):
    response = requests.get(f"https://www.reddit.com/user/{username}/about.json", headers={'user-agent': web_useragent}).json()
    u_id = response.get('data', {}).get('id')
    if u_id is None:
        return None
    else:
        return f't2_{u_id}'


class Invitation:
    def __init__(self, data):
        self.data = data


class Tools:
    def __init__(self, reddit_auth):
        self.headers = {
            'User-Agent': user_agent,
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
        data = json.dumps({
            'channel_url': channel_url,
            'user_id': user_id,
            'duration': duration
        })
        uri = f'{S_REDDIT}/api/v1/channel/kick/user'
        self._handled_req(method='POST', uri=uri, headers=headers, data=data)

    def invite_user(self, channel_url, nicknames):
        assert isinstance(nicknames, list)
        users = []
        for nickname in nicknames:
            users.append({'user_id': _get_user_id(nickname), 'nickname': nickname})
        headers = {'Authorization': f'Bearer {self._reddit_auth._api_token}', **self.headers}
        data = json.dumps({
            'users': users
        })
        url = f'{S_REDDIT}/api/v1/sendbird/group_channels/{channel_url}/invite'
        self._handled_req(method='POST', uri=url, headers=headers, data=data)

    def accept_chat_invite(self, inviation, session_key):
        assert isinstance(inviation, Invitation), 'invitation must be of Invitation taken from get_chat_invites()'
        headers = {'Session-Key': session_key, **self.headers}
        data = json.dumps({
            'user_id': self._reddit_auth.user_id
        })
        url = f'{SB_PROXY_CHATMEDIA}/v3/group_channels/{inviation.data["channel_url"]}/accept'
        return self._handled_req(method='PUT', uri=url, headers=headers, data=data).json

    def get_chat_invites(self, session_key):
        headers = {'Session-Key': session_key, **self.headers}
        params = (
            ('limit', '40'),
            ('order', 'latest_last_message'),
            ('show_member', 'true'),
            ('show_read_receipt', 'true'),
            ('show_delivery_receipt', 'true'),
            ('show_empty', 'true'),
            ('member_state_filter', 'invited_only'),
            ('super_mode', 'all'),
            ('public_mode', 'all'),
            ('unread_filter', 'all'),
            ('hidden_mode', 'unhidden_only'),
            ('show_frozen', 'true'),
        )
        url = f'{SB_PROXY_CHATMEDIA}/v3/users/{self._reddit_auth.user_id}/my_group_channels'
        response = self._handled_req(method='GET', uri=url, headers=headers, params=params).json()
        invitations = []
        for channel in response.get('channels', {}):
            invitations.append(Invitation(channel))
        return invitations

    def leave_chat(self):
        pass

    def create_channel(self, nicknames, group_name, own_name):
        assert isinstance(nicknames, list)
        users = [{"user_id": self._reddit_auth.user_id, "nickname": own_name}]
        for nickname in nicknames:
            users.append({'user_id': _get_user_id(nickname), 'nickname': nickname})
        headers = {'Authorization': f'Bearer {self._reddit_auth._api_token}', **self.headers}
        data = json.dumps({
            'users': users,
            'name': group_name
        })
        url = f'{S_REDDIT}/api/v1/sendbird/group_channels'
        self._handled_req(method='POST', uri=url, headers=headers, data=data)
