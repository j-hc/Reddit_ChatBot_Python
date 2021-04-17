import websocket
from ._utils.rate_limiter import RateLimiter
import time
from ._utils.frame_model import get_frame_data, FrameType
import logging
from threading import Thread
from ._utils import ws_utils
from ._utils.consts import MESG_regular, MESG_snoo, TPST, TPEN, MOBILE_USERAGENT


logging.basicConfig(level=logging.INFO, datefmt='%H:%M', format='%(asctime)s, %(levelname)s: %(message)s')


def _print_chat_(resp, channelid_sub_pairs):
    if resp.type_f == FrameType.MESG:
        print(f"{resp.user.name}@{channelid_sub_pairs.get(resp.channel_url)}: {resp.message}")


class WebSockClient:
    def __init__(self, access_token, user_id, enable_trace=False, print_chat=True, log_websocket_frames=False,
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

        self.logger = logging.getLogger(__name__)
        self.logger.disabled = not other_logging
        websocket.enableTrace(enable_trace)

        ws_url = ws_utils.get_ws_url(self._user_id, access_token)
        self.ws = self._get_ws_app(ws_url)

        self.req_id = int(time.time() * 1000)
        self.own_name = None
        self.print_chat = print_chat
        self.log_websocket_frames = log_websocket_frames
        self.last_err = None
        self.is_logi_err = False
        self.session_key = None

        self._get_current_channels = None

        self.after_message_hooks = []

    def _get_ws_app(self, ws_url):
        ws = websocket.WebSocketApp(ws_url,
                                    on_message=self.on_message,
                                    on_error=self.on_error,
                                    on_close=self.on_close,
                                    on_open=self.on_open,
                                    header={'User-Agent': MOBILE_USERAGENT}
                                    )
        return ws

    def ws_run_forever(self, skip_utf8_validation):
        self.ws.run_forever(ping_interval=15, ping_timeout=5, skip_utf8_validation=skip_utf8_validation)

    def update_ws_app_urls_access_token(self, access_token):
        self.ws.url = ws_utils.get_ws_url(self._user_id, access_token)

    def on_open(self, _):
        self.logger.info("### successfully connected to the websocket ###")

    def on_message(self, _, message):
        resp = get_frame_data(message)
        if self.print_chat:
            _print_chat_(resp, self.channelid_sub_pairs)
        if self.log_websocket_frames:
            self.logger.info(message)
        if resp.type_f == FrameType.LOGI:
            self.logger.info(message)
            self._logi(resp)

        if resp.type_f == FrameType.MESG and resp.user.name in self.global_blacklist_users:
            return

        Thread(target=self._response_loop, args=(resp,), daemon=True).start()

    def _logi(self, resp):
        try:
            logi_err = resp.error
        except AttributeError:
            logi_err = None
        if logi_err is None:
            self.session_key = resp.key
            self.current_channels = self._get_current_channels(limit=100, order='latest_last_message', show_member=True,
                                                               show_read_receipt=True, show_empty=True,
                                                               member_state_filter='joined_only', super_mode='all',
                                                               public_mode='all', unread_filter='all',
                                                               hidden_mode='all', show_frozen=True,
                                                               session_key=self.session_key)
            self.update_channelid_sub_pair()
            self.own_name = resp.nickname
        else:
            self.logger.error(f"err: {resp.message}")
            self.is_logi_err = True

    def update_channelid_sub_pair(self):
        self.channelid_sub_pairs = ws_utils.pair_channel_and_names(channels=self.current_channels)

    def _response_loop(self, resp):
        for func in self.after_message_hooks:
            if func(resp):
                break

    def ws_send_message(self, text, channel_url):
        if self.RateLimiter.is_enabled and self.RateLimiter.check():
            return
        if any(blacklist_word in text.lower() for blacklist_word in self.global_blacklist_words):
            return
        payload = MESG_regular.format(channel_url=channel_url, text=text, req_id=self.req_id)
        self.ws.send(payload)
        self.req_id += 1

    def ws_send_snoomoji(self, snoomoji, channel_url):
        if self.RateLimiter.is_enabled and self.RateLimiter.check():
            return
        payload = MESG_snoo.format(channel_url=channel_url, snoomoji=snoomoji, req_id=self.req_id)
        self.ws.send(payload)
        self.req_id += 1

    def ws_send_typing_indicator(self, channel_url):
        payload = TPST.format(channel_url=channel_url, time=int(time.time() * 1000))
        self.ws.send(payload)

    def ws_stop_typing_indicator(self, channel_url):
        payload = TPEN.format(channel_url=channel_url, time=int(time.time() * 1000))
        self.ws.send(payload)

    def on_error(self, _, error):
        self.logger.error(error)
        self.last_err = error

    def on_close(self, _):
        self.logger.warning("### websocket closed ###")
