import websocket
from .Utils.RateLimiter import RateLimiter
import time
from .Utils.FrameModel.FrameModel import FrameModel
import logging
import _thread as thread
from .Utils import WebSocketUtils


class WebSockClient:
    _SB_ai = '2515BDA8-9D3A-47CF-9325-330BC37ADA13'

    def __init__(self, access_token, user_id, enable_trace=False, print_chat=True, print_websocket_frames=False,
                 other_logging=True, global_blacklist_users=None, global_blacklist_words=None):
        self._user_id = user_id
        if global_blacklist_words is None:
            global_blacklist_words = set()
        if global_blacklist_users is None:
            global_blacklist_users = set()
        assert isinstance(global_blacklist_words, set), "blacklists must be set()s"
        assert isinstance(global_blacklist_users, set), "blacklists must be set()s"
        self.global_blacklist_words = global_blacklist_words
        self.global_blacklist_users = global_blacklist_users

        self.channelid_sub_pairs = {}
        self.RateLimiter = RateLimiter

        logging.basicConfig(level=logging.INFO, datefmt='%H:%M', format='%(asctime)s, %(levelname)s: %(message)s')
        self.logger = logging.getLogger("websocket")
        self.logger.disabled = not other_logging

        websocket.enableTrace(enable_trace)
        socket_base = "wss://sendbirdproxyk8s.chat.redditmedia.com"
        ws_params = {
            "user_id": self._user_id,
            "access_token": access_token,
            "p": "Android",
            "pv": 30,
            "sv": "3.0.144",
            "ai": self._SB_ai,
            "SB-User-Agent": "Android%2Fc3.0.144",
            "active": "1"
        }

        self.ws = self._get_ws_app(WebSocketUtils._get_ws_url(socket_base, ws_params))

        self.ws.on_open = lambda ws: self.on_open(ws)
        # self.ws.on_ping = lambda ws, r: self.on_ping(ws, r)
        # self.ws.on_pong = lambda ws, r: self.on_pong(ws, r)

        self.req_id = int(time.time() * 1000)
        self.own_name = None
        self.print_chat = print_chat
        self.print_websocket_frames = print_websocket_frames
        self._last_err = None

        self._after_message_hooks = []

    def _get_ws_app(self, ws_url):
        ws = websocket.WebSocketApp(ws_url,
                                    on_message=lambda ws, msg: self.on_message(ws, msg),
                                    on_error=lambda ws, msg: self.on_error(ws, msg),
                                    on_close=lambda ws: self.on_close(ws))
        return ws

    def on_open(self, ws):
        self.logger.info("### successfully connected to the websocket ###")

    def after_message_hook(self, func):
        def hook(resp):
            if resp.type_f == "MESG":
                func(resp)
        self._after_message_hooks.append(hook)

    def after_frame_hook(self, func):
        self._after_message_hooks.append(func)

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

        self.after_message_hook(respond)

    def set_welcome_message(self, message, limited_to_channels=None):
        try:
            message.format(nickname="")
        except KeyError as e:
            raise Exception("You need to set a {nickname} key in the welcome message!") from e

        if limited_to_channels is not None and isinstance(limited_to_channels, str):
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

        self.after_message_hook(respond)

    def set_byebye_message(self, message, limited_to_channels=None):
        try:
            message.format(nickname="")
        except KeyError as e:
            raise Exception("You need to set a {nickname} key in the byebye message!") from e

        if limited_to_channels is not None and isinstance(limited_to_channels, str):
            limited_to_channels = [limited_to_channels]
        elif limited_to_channels is None:
            limited_to_channels = []

        def respond(resp):
            if resp.type_f == "SYEV" and (self.channelid_sub_pairs.get(resp.channel_url) in limited_to_channels or not bool(limited_to_channels)):
                try:
                    dispm = resp.channel.disappearing_message
                    nickname = resp.data.nickname
                except AttributeError:
                    return
                response_prepped = message.format(nickname=nickname)
                self.send_message(response_prepped, resp.channel_url)
                return True

        self.after_message_hook(respond)

    def on_message(self, ws, message):
        resp = FrameModel.get_frame_data(message)
        if self.print_chat:
            WebSocketUtils.print_chat_(resp, self.channelid_sub_pairs)
        if self.print_websocket_frames:
            print(message)

        if resp.type_f == "LOGI":
            self.logger.info(message)
            self._logi(resp)

        if resp.type_f == "MESG" and resp.user.name in self.global_blacklist_users:
            return

        thread.start_new_thread(self._response_loop, (resp,))

    def _logi(self, resp):
        try:
            logi_err = resp.error
        except:
            logi_err = False
        if not logi_err:
            self.channelid_sub_pairs = WebSocketUtils._get_current_channels(self._user_id, resp.key)
            self.own_name = resp.nickname
        else:
            self.logger.error(f"err: {resp.message}")

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

    # def send_typing_indicator(self, channel_url):
    #     payload = f'TPST{{"channel_url":"{channel_url}","time":{int(time.time() * 1000)},"req_id":""}}\n'
    #     self.ws.send(payload)

    def on_error(self, ws, error):
        self.logger.error(error)
        self._last_err = error

    def on_close(self, ws):
        self.logger.warning("### websocket closed ###")

    def run_4ever(self, auto_reconnect=True):
        while auto_reconnect:
            self.ws.run_forever(ping_interval=15, ping_timeout=5)
            if isinstance(self._last_err, websocket.WebSocketConnectionClosedException):
                continue
            else:
                return
        self.ws.run_forever(ping_interval=15, ping_timeout=5)

    # def on_ping(self, ws, r):
    #     print("ping")
    #
    # def on_pong(self, ws, r):
    #     print("pong")
