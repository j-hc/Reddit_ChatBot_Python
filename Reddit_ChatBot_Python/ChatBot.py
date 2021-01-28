from .WebSockClient import WebSockClient
# from .Utils.ChatMedia import ChatMedia
import pickle
from .RedditAuthentication import TokenAuth, PasswordAuth
from websocket import WebSocketConnectionClosedException


class ChatBot:
    def __init__(self, authentication, store_session=True, **kwargs):
        assert isinstance(authentication, (TokenAuth, PasswordAuth)), "Wrong Authentication type"
        self._kwargs = kwargs
        self._r_authentication = authentication
        if store_session:
            pkl_n = authentication._api_token if isinstance(authentication, TokenAuth) else authentication.reddit_username
            sb_access_token, user_id = self._load_session(pkl_n)
        else:
            reddit_authentication = self._r_authentication.authenticate()
            sb_access_token, user_id = reddit_authentication['sb_access_token'], reddit_authentication['user_id']

        self._init_websockclient(sb_access_token, user_id)

        # if with_chat_media:  # this is untested
        #     self.ChatMedia = ChatMedia(key=sb_access_token, reddit_api_token=reddit_api_token)

    def _init_websockclient(self, sb_access_token, user_id):
        self.WebSocketClient = WebSockClient(access_token=sb_access_token, user_id=user_id, **self._kwargs)

    def get_chatroom_name_id_pairs(self):
        return self.WebSocketClient.channelid_sub_pairs

    def after_message_hook(self, frame_type='MESG'):
        def after_frame_hook(func):
            def hook(resp):
                if resp.type_f == frame_type:
                    func(resp)
            self.WebSocketClient.after_message_hooks.append(hook)
        return after_frame_hook

    def set_respond_hook(self, input_, response, limited_to_users=None, lower_the_input=False, exclude_itself=True,
                         must_be_equal=True, limited_to_channels=None):

        if limited_to_users is not None and isinstance(limited_to_channels, str):
            limited_to_users = [limited_to_users]
        elif limited_to_users is None:
            limited_to_users = []
        if limited_to_channels is not None and isinstance(limited_to_channels, str):
            limited_to_channels = [limited_to_channels]
        elif limited_to_channels is None:
            limited_to_channels = []

        try:
            response.format(nickname="")
        except KeyError as e:
            raise Exception("You need to set a {nickname} key in welcome message!") from e

        def hook(resp):
            if resp.type_f == "MESG":
                sent_message = resp.message.lower() if lower_the_input else resp.message
                if (resp.user.name in limited_to_users or not bool(limited_to_users)) \
                        and (exclude_itself and resp.user.name != self.WebSocketClient.own_name) \
                        and ((must_be_equal and sent_message == input_) or (not must_be_equal and input_ in sent_message)) \
                        and (self.WebSocketClient.channelid_sub_pairs.get(resp.channel_url) in limited_to_channels or not bool(limited_to_channels)):
                    response_prepped = response.format(nickname=resp.user.name)
                    self.WebSocketClient.ws_send_message(response_prepped, resp.channel_url)
                    return True

        self.WebSocketClient.after_message_hooks.append(hook)

    def set_welcome_message(self, message, limited_to_channels=None):
        try:
            message.format(nickname="", inviter="")
        except KeyError as e:
            raise Exception("Keys should be {nickname} and {inviter}") from e

        if limited_to_channels is not None and isinstance(limited_to_channels, str):
            limited_to_channels = [limited_to_channels]
        elif limited_to_channels is None:
            limited_to_channels = []

        def hook(resp):
            if resp.type_f == "SYEV" and (self.WebSocketClient.channelid_sub_pairs.get(resp.channel_url) in limited_to_channels or not bool(limited_to_channels)):
                try:
                    nickname = resp.data.users[0].nickname
                    inviter = resp.data.users[0].inviter.nickname
                except (AttributeError, IndexError):
                    return
                response_prepped = message.format(nickname=nickname, inviter=inviter)
                self.WebSocketClient.ws_send_snoomoji(response_prepped, resp.channel_url)
                return True

        self.WebSocketClient.after_message_hooks.append(hook)

    def set_farewell_message(self, message, limited_to_channels=None):
        try:
            message.format(nickname="")
        except KeyError as e:
            raise Exception("Key should be {nickname}") from e

        if limited_to_channels is not None and isinstance(limited_to_channels, str):
            limited_to_channels = [limited_to_channels]
        elif limited_to_channels is None:
            limited_to_channels = []

        def hook(resp):
            if resp.type_f == "SYEV" and (self.WebSocketClient.channelid_sub_pairs.get(resp.channel_url) in limited_to_channels or not bool(limited_to_channels)):
                try:
                    dispm = resp.channel.disappearing_message
                    nickname = resp.data.nickname
                except AttributeError:
                    return
                response_prepped = message.format(nickname=nickname)
                self.WebSocketClient.ws_send_message(response_prepped, resp.channel_url)
                return True

        self.WebSocketClient.after_message_hooks.append(hook)

    def send_message(self, text, channel_url):
        self.WebSocketClient.ws_send_message(text, channel_url)

    def send_snoomoji(self, snoomoji, channel_url):
        self.WebSocketClient.ws_send_snoomoji(snoomoji, channel_url)

    def send_typing_indicator(self, channel_url):
        self.WebSocketClient.ws_send_typing_indicator(channel_url)

    def run_4ever(self, auto_reconnect=True, max_retries=100):
        for _ in range(max_retries):
            self.WebSocketClient.ws.run_forever(ping_interval=15, ping_timeout=5)
            if self.WebSocketClient.is_logi_err and isinstance(self._r_authentication, PasswordAuth):
                self.WebSocketClient.logger.info('Re-Authenticating...')
                sb_access_token, user_id = self._load_session(self._r_authentication.reddit_username, force_reauth=True)
                self._init_websockclient(sb_access_token, user_id)
            elif not (auto_reconnect and isinstance(self.WebSocketClient.last_err, WebSocketConnectionClosedException)):
                break
            self.WebSocketClient.logger.info('Auto Reconnecting...')

    def enable_rate_limiter(self, max_calls, period):
        self.WebSocketClient.RateLimiter.is_enabled = True
        self.WebSocketClient.RateLimiter.max_calls = max_calls
        self.WebSocketClient.RateLimiter.period = period

    def _load_session(self, pkl_name, force_reauth=False):
        def get_store_file_handle(pkl_name_, mode_):
            try:
                return open(f'{pkl_name_}-stored.pkl', mode_)
            except FileNotFoundError:
                return None

        session_store_f = get_store_file_handle(pkl_name, 'rb')

        if session_store_f is None or force_reauth:
            session_store_f = get_store_file_handle(pkl_name, 'wb+')
            reddit_authentication = self._r_authentication.authenticate()
            sb_access_token, user_id = reddit_authentication['sb_access_token'], reddit_authentication['user_id']
            pickle.dump(sb_access_token, session_store_f)
            pickle.dump(user_id, session_store_f)
        else:
            sb_access_token = pickle.load(session_store_f)
            user_id = pickle.load(session_store_f)
        session_store_f.close()

        return sb_access_token, user_id
