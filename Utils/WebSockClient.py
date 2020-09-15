import websocket
import time
from .FrameModel.FrameModel import FrameModel
import logging
import _thread as thread


class WebSockClient:
    class RateLimiter:
        is_enabled = False
        max_calls = 0
        period = 0
        _msg_counter = 0
        _period_end_ts = 0

        @staticmethod
        def _check():
            if WebSockClient.RateLimiter._period_end_ts < WebSockClient.RateLimiter._get_current_ts():
                WebSockClient.RateLimiter._msg_counter = 0
                WebSockClient.RateLimiter._create_new_period()

            if WebSockClient.RateLimiter._msg_counter > WebSockClient.RateLimiter.max_calls:
                return True
            else:
                WebSockClient.RateLimiter._msg_counter += 1
                return False

        @staticmethod
        def _create_new_period():
            WebSockClient.RateLimiter._period_end_ts = WebSockClient.RateLimiter._get_current_ts() +\
                                                       WebSockClient.RateLimiter.period * 60

        @staticmethod
        def _get_current_ts():
            return int(time.time())

    def __init__(self, key, ai, user_id, enable_trace=False, channelid_sub_pairs=None, print_chat=True,
                 other_logging=True, global_blacklist_users=None, global_blacklist_words=None):
        if global_blacklist_users is None:
            self.global_blacklist_users = []
        else:
            self.global_blacklist_users = global_blacklist_users
        if global_blacklist_words is None:
            self.global_blacklist_words = []
        else:
            self.global_blacklist_words = global_blacklist_words

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

        self._after_message_hooks = []

    def on_open(self, ws):
        self.logger.info("### successfully connected to the websocket ###")

    def add_after_message_hook(self, func):
        self._after_message_hooks.append(func)

    def set_respond_hook(self, input_, response, limited_to_users=None, lower_the_input=False, exclude_itself=True,
                         must_be_equal=True, quote_parent=False):

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
                    if quote_parent:
                        response_prepped = f'@{resp.user.name}, {response}'
                    else:
                        response_prepped = response
                    self.send_message(response_prepped, resp.channel_url)
                    return True

        self.add_after_message_hook(respond)

    def run_4ever(self, ping_interval=15, ping_timeout=5):
        self.ws.run_forever(ping_interval=ping_interval, ping_timeout=ping_timeout)

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

        thread.start_new_thread(self.response_loop, (resp,))

    def response_loop(self, resp):
        for func in self._after_message_hooks:
            if func(resp):
                break

    def send_message(self, text, channel_url):
        print(WebSockClient.RateLimiter._msg_counter)
        if WebSockClient.RateLimiter.is_enabled and WebSockClient.RateLimiter._check():
            return

        if any(blacklist_word in text.lower() for blacklist_word in self.global_blacklist_words):
            return
        payload = f'MESG{{"channel_url":"{channel_url}","message":"{text}","data":"{{\\"v1\\":{{\\"preview_collapsed\\":false,\\"embed_data\\":{{}},\\"hidden\\":false,\\"highlights\\":[],\\"message_body\\":\\"{text}\\"}}}}","mention_type":"users","req_id":"{self.req_id}"}}\n'
        self.ws.send(payload)
        self.req_id += 1

    def send_snoomoji(self, snoomoji, channel_url):
        payload = f'MESG{{"channel_url":"{channel_url}","message":"","data":"{{\\"v1\\":{{\\"preview_collapsed\\":false,\\"embed_data\\":{{\\"site_name\\":\\"Reddit\\"}},\\"hidden\\":false,\\"snoomoji\\":\\"{snoomoji}\\"}}}}","mention_type":"users","req_id":"{self.req_id}"}}\n'
        self.ws.send(payload)
        self.req_id += 1

    def on_error(self, ws, error):
        self.logger.error(error)
        raise Exception("WEBSOCKET ERROR")

    def on_close(self, ws):
        self.logger.warning("### websocket closed ###")

    # def on_ping(self, ws, r):
    #     print("ping")
    #
    # def on_pong(self, ws, r):
    #     print("pong")
