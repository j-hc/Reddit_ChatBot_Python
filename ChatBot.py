from .Utils.WebSockClient import WebSockClient
from .Utils.ChatMedia import ChatMedia
import requests
import pickle


class ChatBot:
    _SB_ai = '2515BDA8-9D3A-47CF-9325-330BC37ADA13'

    def __init__(self, reddit_api_token, with_chat_media=False, sub_channels=None, store_session=True, **kwargs):
        self.sub_channels = sub_channels
        self.sub_channel_list = {}
        self.headers = {'user-agent': "test v2", 'authorization': f'Bearer {reddit_api_token}'}

        if store_session:
            channelid_sub_pairs, sb_access_token, user_id = self._load_session(reddit_api_token)
        else:
            channelid_sub_pairs, sb_access_token, user_id = self._get_new_session()

        self.WebSocketClient = WebSockClient(key=sb_access_token, ai=self._SB_ai, user_id=user_id,
                                             channelid_sub_pairs=channelid_sub_pairs, **kwargs)
        if with_chat_media:
            self.ChatMedia = ChatMedia(key=sb_access_token, ai=self._SB_ai, reddit_api_token=reddit_api_token)
            # this is untested

    def join_channel(self, sub, channel_url):
        if channel_url.startswith("sendbird_group_channel_"):
            channel_url_ = channel_url
        else:
            channel_url_ = "sendbird_group_channel_" + channel_url
        sub_id = self._get_sub_id(sub)
        data = f'{{"channel_url":"{channel_url_}","subreddit":"{sub_id}"}}'
        resp = requests.post('https://s.reddit.com/api/v1/sendbird/join', headers=self.headers, data=data)
        return resp.text

    def _load_session(self, pkl_name):
        try:
            session_store_f = open(f'{pkl_name}.pkl', 'rb')
            channelid_sub_pairs = pickle.load(session_store_f)
            sb_access_token = pickle.load(session_store_f)
            user_id = pickle.load(session_store_f)
            print("loading from session goes brrr")
        except FileNotFoundError:
            channelid_sub_pairs, sb_access_token, user_id = self._get_new_session()
            session_store_f = open(f'{pkl_name}.pkl', 'wb+')
            pickle.dump(channelid_sub_pairs, session_store_f)
            pickle.dump(sb_access_token, session_store_f)
            pickle.dump(user_id, session_store_f)
        finally:
            session_store_f.close()

        return channelid_sub_pairs, sb_access_token, user_id

    def _get_new_session(self):
        sub_channels = self.sub_channels
        channelid_sub_pairs = {}
        if sub_channels is not None:
            if type(sub_channels) != list:
                sub_channelss = [sub_channels]
            else:
                sub_channelss = sub_channels
            for sub_channel in sub_channelss:
                channel_urls = self._get_sendbird_channel_urls(sub_channel)
                for channel_url in channel_urls:
                    channelid_sub_pairs.update({channel_url: sub_channel})

        sb_access_token = self._get_sendbird_access_token()
        user_id = self._get_user_id()

        return channelid_sub_pairs, sb_access_token, user_id

    def _get_sendbird_access_token(self):
        response = requests.get('https://s.reddit.com/api/v1/sendbird/me', headers=self.headers)
        response.raise_for_status()
        return response.json()['sb_access_token']

    def _get_user_id(self):
        response = requests.get('https://oauth.reddit.com/api/v1/me.json', headers=self.headers)
        response.raise_for_status()
        return 't2_' + response.json().get('id')

    def _get_sub_id(self, sub_name):
        response = requests.get(f'https://oauth.reddit.com/r/{sub_name}/about.json', headers=self.headers)
        response.raise_for_status()
        sub_id = response.json().get('data').get('name')
        if sub_id is None:
            raise Exception('Wrong subreddit name')
        return sub_id

    def _get_sendbird_channel_urls(self, sub_name):
        sub_id = self._get_sub_id(sub_name)
        response = requests.get(f'https://s.reddit.com/api/v1/subreddit/{sub_id}/channels', headers=self.headers)
        response.raise_for_status()
        try:
            rooms = response.json().get('rooms')
            for room in rooms:
                yield room.get('url')
        except (KeyError, IndexError):
            raise Exception('Sub doesnt have any rooms')
