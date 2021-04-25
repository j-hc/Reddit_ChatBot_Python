import requests
from .._utils.consts import SB_PROXY_CHATMEDIA, S_REDDIT, USER_AGENT, SB_User_Agent, SB_ai, WEB_USERAGENT, WWW_REDDIT
import json
from .models import Channel, Message


def _get_user_id(username):
    response = requests.get(f"{WWW_REDDIT}/user/{username}/about.json",
                            headers={'user-agent': WEB_USERAGENT}).json()
    u_id = response.get('data', {}).get('id')
    if u_id is None:
        return None
    else:
        return f't2_{u_id}'


class Tools:
    def __init__(self, reddit_auth):
        self._req_sesh = requests.Session()
        self._req_sesh.headers = {
            'User-Agent': USER_AGENT,
            'SendBird': f'Android,29,3.0.82,{SB_ai}',
            'SB-User-Agent': SB_User_Agent
        }
        self._reddit_auth = reddit_auth
        try:
            _ = self._reddit_auth.reddit_username
            self._is_reauthable = True
        except AttributeError:
            self._is_reauthable = False

    def _handled_req(self, method, uri, **kwargs):
        while True:
            response = self._req_sesh.request(method, uri, **kwargs)
            if response.status_code == 401 and self._is_reauthable:
                new_access_token = self._reddit_auth.refresh_api_token()
                new_headers = kwargs.get('headers', {})
                new_headers.update({'Authorization': f'Bearer {new_access_token}'})
                kwargs.update({'headers': new_headers})
                continue
            elif response.status_code != 200:
                raise Exception(response.json())
            else:
                return response

    def rename_channel(self, name, channel_url, session_key):
        data = json.dumps({
            # 'cover_url': '',
            'name': name,
            # 'data': ''
        })
        uri = f"{SB_PROXY_CHATMEDIA}/v3/group_channels/{channel_url}"
        response = self._handled_req(method='PUT', uri=uri, data=data, headers={'Session-Key': session_key})
        return Channel.from_dict(response.json())

    def delete_message(self, channel_url, msg_id, session_key):
        uri = f"{SB_PROXY_CHATMEDIA}/v3/group_channels/{channel_url}/messages/{msg_id}"
        self._handled_req(method='DELETE', uri=uri, headers={'Session-Key': session_key})

    def kick_user(self, channel_url, user_id, duration):
        data = json.dumps({
            'channel_url': channel_url,
            'user_id': user_id,
            'duration': duration
        })
        uri = f'{S_REDDIT}/api/v1/channel/kick/user'
        self._handled_req(method='POST', uri=uri, headers={'Authorization': f'Bearer {self._reddit_auth.api_token}'},
                          data=data)

    def invite_user(self, channel_url, nicknames):
        assert isinstance(nicknames, list)
        users = []
        for nickname in nicknames:
            users.append({'user_id': _get_user_id(nickname), 'nickname': nickname})
        data = json.dumps({
            'users': users
        })
        url = f'{S_REDDIT}/api/v1/sendbird/group_channels/{channel_url}/invite'
        self._handled_req(method='POST', uri=url, headers={'Authorization': f'Bearer {self._reddit_auth.api_token}'},
                          data=data)

    def accept_chat_invite(self, channel_url, session_key):
        data = json.dumps({
            'user_id': self._reddit_auth.user_id
        })
        url = f'{SB_PROXY_CHATMEDIA}/v3/group_channels/{channel_url}/accept'
        self._handled_req(method='PUT', uri=url, headers={'Session-Key': session_key}, data=data)

    def get_channels(self, limit, order, show_member, show_read_receipt, show_empty, member_state_filter, super_mode,
                     public_mode, unread_filter, hidden_mode, show_frozen, session_key):
        params = {
            'limit': limit,
            'order': order,
            'show_member': show_member,
            'show_read_receipt': show_read_receipt,
            'show_delivery_receipt': 'true',
            'show_empty': show_empty,
            'member_state_filter': member_state_filter,
            'super_mode': super_mode,
            'public_mode': public_mode,
            'unread_filter': unread_filter,
            'hidden_mode': hidden_mode,
            'show_frozen': show_frozen,
        }
        url = f'{SB_PROXY_CHATMEDIA}/v3/users/{self._reddit_auth.user_id}/my_group_channels'
        response = self._handled_req(method='GET', uri=url, headers={'Session-Key': session_key}, params=params)
        return [Channel.from_dict(channel) for channel in response.json()['channels']]

    def leave_chat(self, channel_url, session_key):
        data = json.dumps({
            'user_id': self._reddit_auth.user_id
        })
        url = f'{SB_PROXY_CHATMEDIA}/v3/group_channels/{channel_url}/leave'
        self._handled_req(method='PUT', uri=url, headers={'Session-Key': session_key}, data=data)

    def create_channel(self, nicknames, group_name, own_name):
        users = [{"user_id": self._reddit_auth.user_id, "nickname": own_name}]
        for nickname in nicknames:
            users.append({'user_id': _get_user_id(nickname), 'nickname': nickname})
        data = json.dumps({
            'users': users,
            'name': group_name
        })
        url = f'{S_REDDIT}/api/v1/sendbird/group_channels'
        response = self._handled_req(method='POST', uri=url,
                                     headers={'Authorization': f'Bearer {self._reddit_auth.api_token}'},
                                     data=data)
        return Channel.from_dict(response.json())

    def hide_chat(self, user_id, channel_url, hide_previous_messages, allow_auto_unhide, session_key):
        data = json.dumps({
            'user_id': user_id,
            'hide_previous_messages': hide_previous_messages,
            'allow_auto_unhide': allow_auto_unhide
        })
        self._handled_req(method='PUT', uri=f'{SB_PROXY_CHATMEDIA}/v3/group_channels/{channel_url}/hide',
                          headers={'Session-Key': session_key}, data=data)

    def get_older_messages(self, channel_url, prev_limit, next_limit, reverse, session_key):
        params = {
            'is_sdk': 'true',
            'prev_limit': prev_limit,
            'next_limit': next_limit,
            'include': 'false',
            'reverse': reverse,
            'message_ts': 9007199254740991,
            'with_sorted_meta_array': 'false',
            'include_reactions': 'false',
            'include_thread_info': 'false',
            'include_replies': 'false',
            'include_parent_message_text': 'false'
        }

        response = self._handled_req(method='GET', uri=f'{SB_PROXY_CHATMEDIA}/v3/group_channels/{channel_url}/messages',
                                     headers={'Session-Key': session_key}, params=params)
        return [Message.from_dict(msg) for msg in response.json()['messages']]
