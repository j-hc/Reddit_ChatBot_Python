import websocket
from .RateLimiter import RateLimiter
import time
from .FrameModel.FrameModel import FrameModel
import logging
import _thread as thread
import requests


class WebSockClient:
    def __init__(self, key, ai, user_id, enable_trace=False, print_chat=True,
                 other_logging=True, dont_hook_blocked=False, global_blacklist_users=None, global_blacklist_words=None):
        self._ai = ai
        self._user_id = user_id
        self.dont_hook_blocked = dont_hook_blocked
        if global_blacklist_words is None:
            global_blacklist_words = set()
        if global_blacklist_users is None:
            global_blacklist_users = set()
        assert type(global_blacklist_words) == set, "blacklists must be set()s"
        assert type(global_blacklist_users) == set, "blacklists must be set()s"
        self.global_blacklist_words = global_blacklist_words
        self.global_blacklist_users = global_blacklist_users

        self.channelid_sub_pairs = {}
        self.RateLimiter = RateLimiter

        logging.basicConfig(level=logging.INFO, datefmt='%H:%M', format='%(asctime)s, %(levelname)s: %(message)s')
        self.logger = logging.getLogger("websocket")
        self.logger.disabled = not other_logging

        websocket.enableTrace(enable_trace)
        socket_base = "wss://sendbirdproxy.chat.redditmedia.com"
        params = f"/?p=_&pv=29&sv=3.0.82&ai={self._ai}&user_id={self._user_id}&access_token={key}"

        self.ws = websocket.WebSocketApp(socket_base + params,
                                         on_message=lambda ws, msg: self.on_message(ws, msg),
                                         on_error=lambda ws, msg: self.on_error(ws, msg),
                                         on_close=lambda ws: self.on_close(ws),
                                         )
        self.ws.on_open = lambda ws: self.on_open(ws)
        # self.ws.on_ping = lambda ws, r: self.on_ping(ws, r)
        # self.ws.on_pong = lambda ws, r: self.on_pong(ws, r)

        self.req_id = int(time.time() * 1000)
        self.own_name = None
        self.print_chat = print_chat
        self._last_err = None

        self._after_message_hooks = []

    def on_open(self, ws):
        self.logger.info("### successfully connected to the websocket ###")

    def after_message_hook(self, func):
        self._after_message_hooks.append(func)

    def set_respond_hook(self, input_, response, limited_to_users=None, lower_the_input=False, exclude_itself=True,
                         must_be_equal=True, limited_to_channels=None):

        if limited_to_users is not None and type(limited_to_users) == str:
            limited_to_users = [limited_to_users]
        elif limited_to_users is None:
            limited_to_users = []
        if limited_to_channels is not None and type(limited_to_channels) == str:
            limited_to_channels = [limited_to_channels]
        elif limited_to_channels is None:
            limited_to_channels = []

        try:
            response.format(nickname="")
        except KeyError:
            self.logger.error("You need to set a {nickname} key in welcome message!")
            raise

        def respond(resp):
            if resp.type_f == "MESG":
                sent_message = resp.message.lower() if lower_the_input else resp.message
                if (resp.user.name in limited_to_users or not bool(limited_to_users)) \
                        and (exclude_itself and resp.user.name != self.own_name) \
                        and ((must_be_equal and sent_message == input_) or (not must_be_equal and input_ in sent_message)) \
                        and (self.channelid_sub_pairs.get(resp.channel_url) in limited_to_channels or not bool(limited_to_channels)):
                    response_prepped = response.format(nickname=resp.user.name)
                    self.send_message(response_prepped, resp.channel_url)
                    return True

        self.add_after_message_hook(respond)

    def set_welcome_message(self, message, limited_to_channels=None):
        try:
            message.format(nickname="")
        except KeyError:
            self.logger.error("You need to set a {nickname} key in welcome message!")
            raise

        if limited_to_channels is not None and type(limited_to_channels) == str:
            limited_to_channels = [limited_to_channels]
        elif limited_to_channels is None:
            limited_to_channels = []

        def respond(resp):
            if resp.type_f == "SYEV" and (self.channelid_sub_pairs.get(resp.channel_url) in limited_to_channels or not bool(limited_to_channels)):
                try:
                    invtr = resp.data.inviter.nickname
                    nickname = resp.data.nickname
                except AttributeError:
                    return
                response_prepped = message.format(nickname=nickname)
                self.send_message(response_prepped, resp.channel_url)
                return True

        self.add_after_message_hook(respond)

    def print_chat_(self, resp):
        if resp.type_f == "MESG":
            print(f"{resp.user.name}@{self.channelid_sub_pairs.get(resp.channel_url)}: {resp.message}")

    def on_message(self, ws, message):
        resp = FrameModel.get_frame_data(message)
        if self.print_chat:
            self.print_chat_(resp)

        if resp.type_f == "LOGI":
            self.logger.info(message)
            if not resp.error:
                self.logger.info("Everything is: OK")

                self.channelid_sub_pairs = self._get_current_channels(resp.key)
                self.own_name = resp.nickname
            else:
                self.logger.error(f"err: {resp.message}")

        if resp.type_f == "MESG" and resp.user.name in self.global_blacklist_users \
                or (self.dont_hook_blocked and resp.user.is_blocked_by_me):
            return

        thread.start_new_thread(self._response_loop, (resp,))

    def _response_loop(self, resp):
        for func in self._after_message_hooks:
            if func(resp):
                break

    def send_message(self, text, channel_url):
        if self.RateLimiter.is_enabled and self.RateLimiter._check():
            return
        if any(blacklist_word in text.lower() for blacklist_word in self.global_blacklist_words):
            return
        payload = f'MESG{{"channel_url":"{channel_url}","message":"{text}","data":"{{\\"v1\\":{{\\"preview_collapsed\\":false,\\"embed_data\\":{{}},\\"hidden\\":false,\\"highlights\\":[],\\"message_body\\":\\"{text}\\"}}}}","mention_type":"users","req_id":"{self.req_id}"}}\n'
        self.ws.send(payload)
        self.req_id += 1

    def send_snoomoji(self, snoomoji, channel_url):
        if self.RateLimiter.is_enabled and self.RateLimiter._check():
            return
        payload = f'MESG{{"channel_url":"{channel_url}","message":"","data":"{{\\"v1\\":{{\\"preview_collapsed\\":false,\\"embed_data\\":{{\\"site_name\\":\\"Reddit\\"}},\\"hidden\\":false,\\"snoomoji\\":\\"{snoomoji}\\"}}}}","mention_type":"users","req_id":"{self.req_id}"}}\n'
        self.ws.send(payload)
        self.req_id += 1

    # not working for some reason
    # def send_typing_indicator(self, channel_url):
    #     payload = f'TPST{{"channel_url":"{channel_url}","time":{int(time.time() * 1000)},"req_id":""}}\n'
    #     self.ws.send(payload)

    def on_error(self, ws, error):
        self.logger.error(error)
        self._last_err = error

    def on_close(self, ws):
        self.logger.warning("### websocket closed ###")

    def run_4ever(self, auto_reconnect=True, ping_interval=15, ping_timeout=5):
        while auto_reconnect:
            self.ws.run_forever(ping_interval=ping_interval, ping_timeout=ping_timeout)
            if self._last_err is websocket.WebSocketConnectionClosedException:
                continue
            else:
                return 0
        self.ws.run_forever(ping_interval=ping_interval, ping_timeout=ping_timeout)

    def _get_current_channels(self, session_key):
        headers = {
            'Host': 'sendbirdproxy.chat.redditmedia.com',
            'accept': 'application/json',
            'user-agent': 'Jand/3.0.144',
            'sb-user-agent': 'Android/c3.0.144',
            'sendbird': f'Android,30,3.0.144,{self._ai}',
            'session-key': session_key,
            'request-sent-timestamp': str(int(time.time() * 1000)),
        }
        params = {
            'show_member': 'true',
            'show_frozen': 'true',
            'public_mode': 'all',
            'member_state_filter': 'joined_only',
            'token': '',
            'super_mode': 'super',
            'limit': '40',
            'show_empty': 'true'
        }

        response = requests.get(f'https://sendbirdproxy.chat.redditmedia.com/v3/users/{self._user_id}/my_group_channels',
                                headers=headers, params=params).json()
        channelid_sub_pairs = {}
        for channel in response.get('channels'):
            channelid_sub_pairs.update({channel['channel']['channel_url']: channel['channel']['name']})
        return channelid_sub_pairs

    # def on_ping(self, ws, r):
    #     print("ping")
    #
    # def on_pong(self, ws, r):
    #     print("pong")
