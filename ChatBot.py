from .Utils.WebSockClient import WebSockClient
from .Utils.ChatMedia import ChatMedia
import requests


class ChatBot:
    _SB_ai = '2515BDA8-9D3A-47CF-9325-330BC37ADA13'

    def __init__(self, reddit_api_token, with_chat_media=False, sub_channels=None, **kwargs):
        self.headers = {'user-agent': "test v2", 'authorization': f'Bearer {reddit_api_token}'}

        self.channelid_sub_pairs = {}
        if sub_channels is not None:
            if type(sub_channels) != list:
                sub_channels = [sub_channels]
            for sub_channel in sub_channels:
                channel_url = self._get_sendbird_channel_url(sub_channel)
                self.channelid_sub_pairs.update({channel_url: sub_channel})
        sb_access_token = self._get_sendbird_access_token()
        user_id = self._get_user_id()

        self.WebSocketClient = WebSockClient(key=sb_access_token, ai=self._SB_ai, user_id=user_id,
                                             channelid_sub_pairs=self.channelid_sub_pairs, **kwargs)
        if with_chat_media:
            self.ChatMedia = ChatMedia(key=sb_access_token, ai=self._SB_ai, reddit_api_token=reddit_api_token)

    def _get_sendbird_access_token(self):
        response = requests.get('https://s.reddit.com/api/v1/sendbird/me', headers=self.headers)
        response.raise_for_status()
        return response.json()['sb_access_token']

    def _get_user_id(self):
        response = requests.get('https://oauth.reddit.com/api/v1/me.json', headers=self.headers)
        response.raise_for_status()
        return 't2_' + response.json().get('id')

    def _get_sub_user_id(self, sub_name):
        response = requests.get(f'https://oauth.reddit.com/r/{sub_name}/about.json', headers=self.headers)
        response.raise_for_status()
        sub_id = response.json().get('data').get('name')
        if sub_id is None:
            raise Exception('Wrong subreddit name')
        return sub_id

    def _get_sendbird_channel_url(self, sub_name):
        sub_id = self._get_sub_user_id(sub_name)
        response = requests.get(f'https://s.reddit.com/api/v1/subreddit/{sub_id}/channels', headers=self.headers)
        response.raise_for_status()
        try:
            return response.json().get('rooms')[0].get('url')
        except (KeyError, IndexError):
            raise Exception('This sub doesnt have any rooms')
