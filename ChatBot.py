from .Utils.WebSockClient import WebSockClient
from .Utils.ChatMedia import ChatMedia
import requests


class ChatBot:
    SB_ai = '2515BDA8-9D3A-47CF-9325-330BC37ADA13'

    def __init__(self, reddit_api_token, with_chat_media=False, **kwargs):
        self.headers = {
            'user-agent': "test v2",
            'authorization': f'Bearer {reddit_api_token}',
        }

        sb_access_token = self.get_sendbird_access_token()
        user_id = self.get_user_id()

        self.WebSocketClient = WebSockClient(key=sb_access_token, ai=self.SB_ai, user_id=user_id, **kwargs)
        if with_chat_media:
            self.ChatMedia = ChatMedia(key=sb_access_token, ai=self.SB_ai, reddit_api_token=reddit_api_token)

    def get_sendbird_access_token(self):
        response = requests.get('https://s.reddit.com/api/v1/sendbird/me', headers=self.headers)
        return response.json()['sb_access_token']

    def get_user_id(self):
        response = requests.get('https://oauth.reddit.com/api/v1/me', headers=self.headers)
        if response.status_code == 200:
            return 't2_' + response.json().get('id')
        else:
            raise Exception("Token Wrong?")
