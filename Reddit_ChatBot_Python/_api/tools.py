import requests
from .._utils.consts import *
import json
from .models import Channel, Message, Members, BannedUsers
from typing import Callable, Optional
import logging


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
        self.session_key_getter: Optional[Callable[[], str]] = None
        self._req_sesh.headers = {
            'User-Agent': USER_AGENT,
            'SendBird': f'Android,31,3.0.168,{SB_ai}',
            'SB-User-Agent': SB_User_Agent,
        }

    def _handled_req(self, method: str, uri: str, chatmedia: bool, **kwargs) -> requests.Response:
        while self._is_running:
            if chatmedia:
                headers = {
                    'User-Agent': USER_AGENT,
                    'SendBird': f'Android,31,3.0.168,{SB_ai}',
                    'SB-User-Agent': SB_User_Agent,
                    'Session-Key': self.session_key_getter()
                }
            else:
                headers = {
                    'User-Agent': MOBILE_USERAGENT,
                    'Authorization': f'Bearer {self._reddit_auth.api_token}',
                    'Content-Type': 'application/json',
                }
            response = self._req_sesh.request(method, uri, headers=headers, **kwargs)
            if response.status_code == 401 and self._reddit_auth.is_reauthable:
                new_access_token = self._reddit_auth.refresh_api_token()
                headers.update({'Authorization': f'Bearer {new_access_token}'})
                continue
            elif response.status_code != 200:
                raise logging.error(response.json())
            else:
                return response
        raise Exception("Cannot do that without running the bot first")

    def send_reaction(self, reaction_icon_key, msg_id, channel_url):
        data = json.dumps({
            "id": "7628b2213978",
            "variables": {
                "channelSendbirdId": channel_url,
                "messageSendbirdId": str(msg_id),
                "reactionIconKey": reaction_icon_key,
                "type": "ADD"
            }
        })
        self._handled_req(method='POST', uri=GQL_REDDIT, chatmedia=False, data=data)

    def delete_reaction(self, reaction_icon_key, msg_id, channel_url):
        data = json.dumps({
            "id": "7628b2213978",
            "variables": {
                "channelSendbirdId": channel_url,
                "messageSendbirdId": msg_id,
                "reactionIconKey": reaction_icon_key,
                "type": "DELETE"
            }
        })
        self._handled_req(method='POST', uri=GQL_REDDIT, chatmedia=False, data=data)

    def rename_channel(self, name, channel_url):
        data = json.dumps({'name': name})
        response = self._handled_req(method='PUT', uri=f"{SB_PROXY_CHATMEDIA}/v3/group_channels/{channel_url}",
                                     chatmedia=True,
                                     data=data)
        return Channel(response.json())

    def delete_message(self, channel_url, msg_id):
        self._handled_req(method='DELETE',
                          uri=f"{SB_PROXY_CHATMEDIA}/v3/group_channels/{channel_url}/messages/{msg_id}",
                          chatmedia=True)

    def kick_user(self, channel_url, user_id, duration):
        data = json.dumps({
            'channel_url': channel_url,
            'user_id': user_id,
            'duration': duration
        })
        self._handled_req(method='POST', uri=f'{S_REDDIT}/api/v1/channel/kick/user',
                          chatmedia=False,
                          data=data)

    def invite_user(self, channel_url, nicknames):
        if isinstance(nicknames, str):
            nicknames = [nicknames]
        users = []
        for nickname in nicknames:
            users.append({'user_id': _get_user_id(nickname), 'nickname': nickname})
        data = json.dumps({'users': users})
        self._handled_req(method='POST', uri=f'{S_REDDIT}/api/v1/sendbird/group_channels/{channel_url}/invite',
                          chatmedia=False,
                          data=data)

    def accept_chat_invite(self, channel_url):
        data = json.dumps({
            'user_id': self._reddit_auth.user_id
        })
        response = self._handled_req(method='PUT', uri=f'{SB_PROXY_CHATMEDIA}/v3/group_channels/{channel_url}/accept',
                                     chatmedia=True, data=data)
        return Channel(response.json())

    def get_channels(self, limit, order, show_member, show_read_receipt, show_empty, member_state_filter, super_mode,
                     public_mode, unread_filter, hidden_mode, show_frozen):
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
        response = self._handled_req(method='GET',
                                     uri=f'{SB_PROXY_CHATMEDIA}/v3/users/{self._reddit_auth.user_id}/my_group_channels',
                                     chatmedia=True, params=params)
        return [Channel(channel) for channel in response.json()['channels']]

    def get_members(self, channel_url, next_token, limit, order, member_state_filter, nickname_startswith):
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
                                     chatmedia=True, params=params)
        return Members(response.json())

    def get_banned_members(self, channel_url, limit):
        params = {
            'limit': limit
        }
        response = self._handled_req(method='GET', uri=f'{SB_PROXY_CHATMEDIA}/v3/group_channels/{channel_url}/ban',
                                     chatmedia=True, params=params)
        return BannedUsers(response.json())

    def leave_chat(self, channel_url):
        data = json.dumps({
            'user_id': self._reddit_auth.user_id
        })
        self._handled_req(method='PUT', uri=f'{SB_PROXY_CHATMEDIA}/v3/group_channels/{channel_url}/leave',
                          chatmedia=True, data=data)

    def create_channel(self, nicknames, group_name, own_name):
        users = [{"user_id": self._reddit_auth.user_id, "nickname": own_name}]
        for nickname in nicknames:
            users.append({'user_id': _get_user_id(nickname), 'nickname': nickname})
        data = json.dumps({
            'users': users,
            'name': group_name
        })
        response = self._handled_req(method='POST', uri=f'{S_REDDIT}/api/v1/sendbird/group_channels',
                                     chatmedia=False,
                                     data=data)
        return Channel(response.json())

    def hide_chat(self, user_id, channel_url, hide_previous_messages, allow_auto_unhide):
        data = json.dumps({
            'user_id': user_id,
            'hide_previous_messages': hide_previous_messages,
            'allow_auto_unhide': allow_auto_unhide
        })
        self._handled_req(method='PUT', uri=f'{SB_PROXY_CHATMEDIA}/v3/group_channels/{channel_url}/hide',
                          chatmedia=True, data=data)

    def get_older_messages(self, channel_url, message_ts, custom_types, prev_limit, next_limit, reverse):
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
                                     chatmedia=True, params=params)
        return [Message(msg) for msg in response.json()['messages']]

    def mute_user(self, channel_url, user_id, duration, description):
        data = json.dumps({
            'user_id': user_id,
            'seconds': duration,
            'description': description
        })
        self._handled_req(method='POST', uri=f"{SB_PROXY_CHATMEDIA}/v3/group_channels/{channel_url}/mute",
                          chatmedia=True, data=data)

    def unmute_user(self, channel_url, user_id):
        self._handled_req(method='DELETE', uri=f"{SB_PROXY_CHATMEDIA}/v3/group_channels/{channel_url}/mute/{user_id}",
                          chatmedia=True)

    def set_channel_frozen_status(self, channel_url, is_frozen):
        data = json.dumps({
            'freeze': is_frozen,
        })
        self._handled_req(method='PUT',
                          uri=f"{SB_PROXY_CHATMEDIA}/v3/group_channels/{channel_url}/freeze",
                          chatmedia=True, data=data)

    def delete_channel(self, channel_url):
        self._handled_req(method='DELETE',
                          uri=f"{SB_PROXY_CHATMEDIA}/v3/group_channels/{channel_url}",
                          chatmedia=True)
