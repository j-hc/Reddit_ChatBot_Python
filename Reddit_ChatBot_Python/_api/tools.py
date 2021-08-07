import requests
from .._utils.consts import SB_PROXY_CHATMEDIA, S_REDDIT, USER_AGENT, SB_User_Agent, SB_ai, WEB_USERAGENT, WWW_REDDIT
import json
from .models import Channel, Message, Members


def _get_user_id(username):
    response = requests.get(f"{WWW_REDDIT}/user/{username}/about.json", headers={'user-agent': WEB_USERAGENT}).json()
    u_id = response.get('data', {}).get('id')
    if u_id is None:
        return None
    else:
        return f't2_{u_id}'


class Tools:
    def __init__(self, reddit_auth):
        self._is_running = False

        self._reddit_auth = reddit_auth
        self._req_sesh = requests.Session()
        self._req_sesh.headers = {
            'User-Agent': USER_AGENT,
            'SendBird': f'Android,29,3.0.82,{SB_ai}',
            'SB-User-Agent': SB_User_Agent
        }
        try:
            _ = self._reddit_auth.reddit_username
            self._is_reauthable = True
        except AttributeError:
            self._is_reauthable = False

    def _handled_req(self, method, uri, **kwargs):
        while self._is_running:
            response = self._req_sesh.request(method, uri, **kwargs)
            if response.status_code == 401 and self._is_reauthable:
                new_access_token = self._reddit_auth.refresh_api_token()
                new_headers = kwargs.get('headers', {})
                new_headers.update({'Authorization': f'Bearer {new_access_token}'})
                kwargs.update({'headers': new_headers})
                continue
            elif response.status_code != 200:
                raise Exception(response.text)
            else:
                return response
        raise Exception("Cannot do that without running the bot first")

    def rename_channel(self, name, channel_url, session_key):
        data = json.dumps({
            'name': name,
        })
        response = self._handled_req(method='PUT', uri=f"{SB_PROXY_CHATMEDIA}/v3/group_channels/{channel_url}",
                                     headers={'Session-Key': session_key},
                                     data=data)
        return Channel._from_dict(response.json())

    def delete_message(self, channel_url, msg_id, session_key):
        self._handled_req(method='DELETE',
                          uri=f"{SB_PROXY_CHATMEDIA}/v3/group_channels/{channel_url}/messages/{msg_id}",
                          headers={'Session-Key': session_key})

    def kick_user(self, channel_url, user_id, duration):
        data = json.dumps({
            'channel_url': channel_url,
            'user_id': user_id,
            'duration': duration
        })
        self._handled_req(method='POST', uri=f'{S_REDDIT}/api/v1/channel/kick/user',
                          headers={'Authorization': f'Bearer {self._reddit_auth.api_token}'},
                          data=data)

    def invite_user(self, channel_url, nicknames):
        assert isinstance(nicknames, list)
        users = []
        for nickname in nicknames:
            users.append({'user_id': _get_user_id(nickname), 'nickname': nickname})
        data = json.dumps({
            'users': users
        })
        self._handled_req(method='POST', uri=f'{S_REDDIT}/api/v1/sendbird/group_channels/{channel_url}/invite',
                          headers={'Authorization': f'Bearer {self._reddit_auth.api_token}'},
                          data=data)

    def accept_chat_invite(self, channel_url, session_key):
        data = json.dumps({
            'user_id': self._reddit_auth.user_id
        })
        self._handled_req(method='PUT', uri=f'{SB_PROXY_CHATMEDIA}/v3/group_channels/{channel_url}/accept',
                          headers={'Session-Key': session_key}, data=data)

    def get_channels(self, limit, order, show_member, show_read_receipt, show_empty, member_state_filter, super_mode,
                     public_mode, unread_filter, hidden_mode, show_frozen, custom_types, session_key):
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
            'custom_types': custom_types
        }
        response = self._handled_req(method='GET',
                                     uri=f'{SB_PROXY_CHATMEDIA}/v3/users/{self._reddit_auth.user_id}/my_group_channels',
                                     headers={'Session-Key': session_key}, params=params)
        return [Channel._from_dict(channel) for channel in response.json()['channels']]

    def get_members(self, channel_url, next_token, limit, order, member_state_filter, nickname_startswith, session_key):
        params = {
            'token': next_token,
            'limit': limit,
            'order': order,
            'muted_member_filter': 'all',
            'member_state_filter': member_state_filter,
            'show_member_is_muted': 'true',
            'show_read_receipt': 'true',
            'show_delivery_receipt': 'true',
            'nickname_startswith': nickname_startswith
        }
        response = self._handled_req(method='GET', uri=f'{SB_PROXY_CHATMEDIA}/v3/group_channels/{channel_url}/members',
                                     headers={'Session-Key': session_key}, params=params)
        return Members._from_dict(response.json())

    def leave_chat(self, channel_url, session_key):
        data = json.dumps({
            'user_id': self._reddit_auth.user_id
        })
        self._handled_req(method='PUT', uri=f'{SB_PROXY_CHATMEDIA}/v3/group_channels/{channel_url}/leave',
                          headers={'Session-Key': session_key}, data=data)

    def create_channel(self, nicknames, group_name, own_name):
        users = [{"user_id": self._reddit_auth.user_id, "nickname": own_name}]
        for nickname in nicknames:
            users.append({'user_id': _get_user_id(nickname), 'nickname': nickname})
        data = json.dumps({
            'users': users,
            'name': group_name
        })
        response = self._handled_req(method='POST', uri=f'{S_REDDIT}/api/v1/sendbird/group_channels',
                                     headers={'Authorization': f'Bearer {self._reddit_auth.api_token}'},
                                     data=data)
        return Channel._from_dict(response.json())

    def hide_chat(self, user_id, channel_url, hide_previous_messages, allow_auto_unhide, session_key):
        data = json.dumps({
            'user_id': user_id,
            'hide_previous_messages': hide_previous_messages,
            'allow_auto_unhide': allow_auto_unhide
        })
        self._handled_req(method='PUT', uri=f'{SB_PROXY_CHATMEDIA}/v3/group_channels/{channel_url}/hide',
                          headers={'Session-Key': session_key}, data=data)

    def get_older_messages(self, channel_url, message_ts, custom_types, prev_limit, next_limit, reverse, session_key):
        params = {
            'is_sdk': 'true',
            'prev_limit': prev_limit,
            'next_limit': next_limit,
            'include': 'false',
            'reverse': reverse,
            'message_ts': message_ts,
            'custom_types': custom_types,
            'with_sorted_meta_array': 'false',
            'include_reactions': 'false',
            'include_thread_info': 'false',
            'include_replies': 'false',
            'include_parent_message_text': 'false'
        }

        response = self._handled_req(method='GET', uri=f'{SB_PROXY_CHATMEDIA}/v3/group_channels/{channel_url}/messages',
                                     headers={'Session-Key': session_key}, params=params)
        return [Message._from_dict(msg) for msg in response.json()['messages']]
