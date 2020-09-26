import websocket
from .RateLimiter import RateLimiter
import time
from .FrameModel.FrameModel import FrameModel
import logging
import _thread as thread


class WebSockClient:
    def __init__(self, key, ai, user_id, enable_trace=False, channelid_sub_pairs=None, print_chat=True,
                 other_logging=True, global_blacklist_users=None, global_blacklist_words=None):
        if global_blacklist_words is None:
            global_blacklist_words = set()
        if global_blacklist_users is None:
            global_blacklist_users = set()

        self.global_blacklist_words = global_blacklist_words
        self.global_blacklist_users = global_blacklist_users

        self._auto_reconnect = True
        self.RateLimiter = RateLimiter

        logging.basicConfig(level=logging.INFO, datefmt='%H:%M', format='%(asctime)s, %(levelname)s: %(message)s')
        self.logger = logging.getLogger("websocket")
        self.logger.disabled = not other_logging
        self.channelid_sub_pairs = channelid_sub_pairs
        websocket.enableTrace(enable_trace)
        socket_base = "wss://sendbirdproxy.chat.redditmedia.com"
        params = f"/?p=_&pv=29&sv=3.0.82&ai={ai}&user_id={user_id}&access_token={key}"

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

    def add_after_message_hook(self, func):
        self._after_message_hooks.append(func)

    def set_respond_hook(self, input_, response, limited_to_users=None, lower_the_input=False, exclude_itself=True,
                         must_be_equal=True):

        if limited_to_users is not None and type(limited_to_users) == str:
            limited_to_users = [limited_to_users]
        elif limited_to_users is None:
            limited_to_users = []

        def respond(resp):
            if resp.type_f == "MESG":
                sent_message = resp.message.lower() if lower_the_input else resp.message
                if (resp.user.name in limited_to_users or not bool(limited_to_users)) \
                        and (exclude_itself and resp.user.name != self.own_name) \
                        and ((must_be_equal and sent_message == input_) or (not must_be_equal and input_ in sent_message)):
                    response_prepped = response.format(nickname=f"{resp.user.name}")
                    self.send_message(response_prepped, resp.channel_url)
                    return True

        self.add_after_message_hook(respond)

    def set_welcome_message(self, message):
        try:
            message.format(nickname="")
        except KeyError:
            self.logger.error("You need to set a {nickname} key in welcome message!")
            raise

        def respond(resp):
            if resp.type_f == "SYEV":
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
                self.own_name = resp.nickname
            else:
                self.logger.error(f"err: {resp.message}")

        if resp.type_f == "MESG" and resp.user.name in self.global_blacklist_users:
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

    # def send_typing_indicator(self, channel_url):  # not working for some reason
    #     payload = f'TPST{{"channel_url":"{channel_url}","time":{int(time.time() * 1000)},"req_id":""}}\n'
    #     self.ws.send(payload)

    def on_error(self, ws, error):
        self.logger.error(error)
        self._last_err = error

    def on_close(self, ws):
        self.logger.warning("### websocket closed ###")
        if self._auto_reconnect and self._last_err == "Connection is already closed.":
            self.logger.info("Auto re-connecting")
            self.run_4ever()

    def run_4ever(self, auto_reconnect=True, ping_interval=15, ping_timeout=5):
        self.ws.run_forever(ping_interval=ping_interval, ping_timeout=ping_timeout)
        self._auto_reconnect = auto_reconnect

    # def on_ping(self, ws, r):
    #     print("ping")
    #
    # def on_pong(self, ws, r):
    #     print("pong")
