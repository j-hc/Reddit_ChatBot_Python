from .WebSockClient import WebSockClient
# from .Utils.ChatMedia import ChatMedia
import requests
import pickle
from .RedditAuthentication import TokenAuth, PasswordAuth


class ChatBot:
    REDDIT_OAUTH_HOST = "https://oauth.reddit.com"
    REDDIT_SENDBIRD_HOST = "https://s.reddit.com"

    def __init__(self, authentication, with_chat_media=False, store_session=True, **kwargs):
        assert isinstance(authentication, (TokenAuth, PasswordAuth)), "Wrong Authentication type"
        self.headers = {'User-Agent': "Reddit/Version 2020.41.1/Build 296539/Android 11"}
        self.authentication = authentication
        if store_session:
            pkl_n = authentication.token if isinstance(authentication, TokenAuth) else authentication.reddit_username
            sb_access_token, user_id = self._load_session(pkl_n)
        else:
            sb_access_token, user_id = self._get_new_session()

        self.WebSocketClient = WebSockClient(access_token=sb_access_token, user_id=user_id, **kwargs)

        # if with_chat_media:  # this is untested
        #     self.ChatMedia = ChatMedia(key=sb_access_token, ai=self._SB_ai, reddit_api_token=reddit_api_token)

    def _load_session(self, pkl_name):
        try:
            session_store_f = open(f'{pkl_name}-stored.pkl', 'rb')
            sb_access_token = pickle.load(session_store_f)
            user_id = pickle.load(session_store_f)
            print("loading from session goes brrr")
        except FileNotFoundError:
            session_store_f = open(f'{pkl_name}-stored.pkl', 'wb+')
            sb_access_token, user_id = self._get_new_session()
            pickle.dump(sb_access_token, session_store_f)
            pickle.dump(user_id, session_store_f)
        finally:
            session_store_f.close()

        return sb_access_token, user_id

    def _get_new_session(self):
        reddit_api_token = self.authentication.authenticate()
        self.headers.update({'Authorization': f'Bearer {reddit_api_token}'})
        sb_access_token = self._get_sendbird_access_token()
        user_id = self._get_user_id()
        return sb_access_token, user_id

    def _get_sendbird_access_token(self):
        response = requests.get(f'{ChatBot.REDDIT_SENDBIRD_HOST}/api/v1/sendbird/me', headers=self.headers)
        response.raise_for_status()
        return response.json()['sb_access_token']

    def _get_user_id(self):
        response = requests.get(f'{ChatBot.REDDIT_OAUTH_HOST}/api/v1/me.json', headers=self.headers)
        response.raise_for_status()
        return 't2_' + response.json()['id']



    #  LEGACY STUFF
    # def join_channel(self, sub, channel_url):
    #     if channel_url.startswith("sendbird_group_channel_"):
    #         channel_url_ = channel_url
    #     else:
    #         channel_url_ = "sendbird_group_channel_" + channel_url
    #     sub_id = self._get_sub_id(sub)
    #     data = f'{{"channel_url":"{channel_url_}","subreddit":"{sub_id}"}}'
    #     resp = requests.post(f'{ChatBot.REDDIT_SENDBIRD_HOST}/api/v1/sendbird/join', headers=self.headers, data=data)
    #     return resp.text

    # def get_sendbird_channel_urls(self, sub_name):
    #     sub_id = self._get_sub_id(sub_name)
    #     response = requests.get(f'{ChatBot.REDDIT_SENDBIRD_HOST}/api/v1/subreddit/{sub_id}/channels', headers=self.headers)
    #     response.raise_for_status()
    #     try:
    #         rooms = response.json().get('rooms')
    #         for room in rooms:
    #             yield room.get('url')
    #     except (KeyError, IndexError):
    #         raise Exception('Sub doesnt have any rooms')

    # def _get_sub_id(self, sub_name):
    #     response = requests.get(f'{ChatBot.REDDIT_OAUTH_HOST}/r/{sub_name}/about.json', headers=self.headers)
    #     response.raise_for_status()
    #     sub_id = response.json().get('data').get('name')
    #     if sub_id is None:
    #         raise Exception('Wrong subreddit name')
    #     return sub_id
