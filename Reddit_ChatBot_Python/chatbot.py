from .ws_client import WebSockClient
import pickle
from .reddit_auth import _RedditAuthBase, TokenAuth, PasswordAuth
from websocket import WebSocketConnectionClosedException
from ._api.tools import Tools
from ._api.models import Channel, Message
from typing import Dict, List, Optional
from ._utils.frame_model import FrameType, FrameModel
from ._events import Events


def _get_locals_without_self(locals_):
    del locals_['self']
    return locals_


class ChatBot:
    def __init__(self, authentication: _RedditAuthBase, store_session: bool = True, **kwargs):
        self._r_authentication = authentication
        self._store_session = store_session
        if store_session:
            if isinstance(authentication, TokenAuth):
                pkl_n = authentication.api_token
            elif isinstance(authentication, PasswordAuth):
                pkl_n = authentication.reddit_username
            else:
                pkl_n = None
            sb_access_token, user_id = self._load_session(pkl_n)
        else:
            reddit_authentication = self._r_authentication.authenticate()
            sb_access_token, user_id = reddit_authentication['sb_access_token'], reddit_authentication['user_id']

        self._tools = Tools(self._r_authentication)
        self.WebSocketClient = WebSockClient(access_token=sb_access_token, user_id=user_id,
                                             get_current_channels=self._tools.get_channels, **kwargs)

        self.event = Events(self.WebSocketClient)

    def get_chatroom_name_id_pairs(self) -> Dict[str, str]:
        return self.WebSocketClient.channelid_sub_pairs

    def get_channelurl_by_name(self, channel_name: str):
        return next(key for key, val in self.WebSocketClient.channelid_sub_pairs.items() if val == channel_name)

    def set_respond_hook(self, input_: str,
                         response: str,
                         limited_to_users: List[str] = None,
                         lower_the_input: bool = False,
                         exclude_itself: bool = True,
                         must_be_equal: bool = True,
                         limited_to_channels: List[str] = None
                         ) -> None:
        if limited_to_channels is None:
            limited_to_channels = []
        if limited_to_users is None:
            limited_to_users = []
        try:
            response.format(nickname="")
        except KeyError as e:
            raise Exception("You need to set a {nickname} key in welcome message!") from e

        def hook(resp: FrameModel) -> Optional[bool]:
            sent_message = resp.message.lower() if lower_the_input else resp.message
            if (resp.user.name in limited_to_users or not bool(limited_to_users)) \
                    and (exclude_itself and resp.user.name != self.WebSocketClient.own_name) \
                    and ((must_be_equal and sent_message == input_) or (not must_be_equal and input_ in sent_message)) \
                    and (self.WebSocketClient.channelid_sub_pairs.get(
                resp.channel_url) in limited_to_channels or not bool(limited_to_channels)):
                response_prepped = response.format(nickname=resp.user.name)
                self.WebSocketClient.ws_send_message(response_prepped, resp.channel_url)
                return True

        self.event.on_any(frame_type=FrameType.MESG)(hook)

    def set_welcome_message(self, message: str, limited_to_channels: List[str] = None) -> None:
        if limited_to_channels is None:
            limited_to_channels = []
        try:
            message.format(nickname="", inviter="")
        except KeyError as e:
            raise Exception("Keys should be {nickname} and {inviter}") from e

        def hook(resp: FrameModel) -> Optional[bool]:
            if self.WebSocketClient.channelid_sub_pairs.get(resp.channel_url) in limited_to_channels or \
                    not bool(limited_to_channels):
                response_prepped = message.format(nickname=resp.data.users[0].nickname,
                                                  inviter=resp.data.users[0].inviter.nickname)
                self.WebSocketClient.ws_send_message(response_prepped, resp.channel_url)
                return True

        self.event.on_user_joined(hook)

    def set_farewell_message(self, message: str, limited_to_channels: List[str] = None) -> None:
        if limited_to_channels is None:
            limited_to_channels = []
        try:
            message.format(nickname="")
        except KeyError as e:
            raise Exception("Key should be {nickname}") from e

        def hook(resp: FrameModel) -> Optional[bool]:
            if self.WebSocketClient.channelid_sub_pairs.get(resp.channel_url) in limited_to_channels or \
                    not bool(limited_to_channels):
                response_prepped = message.format(nickname=resp.data.nickname)
                self.WebSocketClient.ws_send_message(response_prepped, resp.channel_url)
                return True

        self.event.on_user_left(hook)

    def send_message(self, text: str, channel_url: str) -> None:
        self.WebSocketClient.ws_send_message(text, channel_url)

    def send_snoomoji(self, snoomoji: str, channel_url: str) -> None:
        self.WebSocketClient.ws_send_snoomoji(snoomoji, channel_url)

    def send_gif(self, gif_url: str, channel_url: str) -> None:
        self.WebSocketClient.ws_send_gif(gif_url, channel_url)

    def send_typing_indicator(self, channel_url: str) -> None:
        self.WebSocketClient.ws_send_typing_indicator(channel_url)

    def stop_typing_indicator(self, channel_url: str) -> None:
        self.WebSocketClient.ws_stop_typing_indicator(channel_url)

    def run_4ever(self, auto_reconnect: bool = True, max_retries: int = 500, disable_ssl_verification: bool = False,
                  skip_utf8_validation=True, **kwargs) -> None:
        if disable_ssl_verification:
            import ssl
            sslopt = {"cert_reqs": ssl.CERT_NONE}
        else:
            sslopt = None

        for _ in range(max_retries):
            self.WebSocketClient.ws.run_forever(ping_interval=15, ping_timeout=5,
                                                skip_utf8_validation=skip_utf8_validation,
                                                sslopt=sslopt,
                                                **kwargs
                                                # ping_payload="{active:1}"
                                                )
            if self.WebSocketClient.is_logi_err and isinstance(self._r_authentication, PasswordAuth):
                self.WebSocketClient.logger.info("Re-Authenticating...")
                if self._store_session:
                    sb_access_token, _ = self._load_session(self._r_authentication.reddit_username, force_reauth=True)
                else:
                    sb_access_token = self._r_authentication.authenticate()['sb_access_token']
                self.WebSocketClient.update_ws_app_urls_access_token(sb_access_token)
            elif not (auto_reconnect and isinstance(self.WebSocketClient.last_err, WebSocketConnectionClosedException)):
                break
            self.WebSocketClient.logger.info("Auto Re-Connecting...")

    def close(self):
        self.WebSocketClient.ws.close()

    def kick_user(self, channel_url: str, user_id: str, duration: int) -> None:
        self._tools.kick_user(**_get_locals_without_self(locals()))

    def delete_mesg(self, channel_url: str, msg_id: str) -> None:
        self._tools.delete_message(**_get_locals_without_self(locals()), session_key=self.WebSocketClient.session_key)

    def invite_user_to_channel(self, channel_url: str, nicknames: List[str]) -> None:
        self._tools.invite_user(**_get_locals_without_self(locals()))

    def get_chat_invites(self) -> List[Channel]:
        return self.get_channels(member_state_filter="invited_only")

    def get_channels(self, limit: int = 100, order: str = "latest_last_message", show_member: bool = True,
                     show_read_receipt: bool = True, show_empty: bool = True, member_state_filter: str = "joined_only",
                     super_mode: str = "all", public_mode: str = "all", unread_filter: str = "all",
                     hidden_mode: str = "unhidden_only", show_frozen: bool = True) -> List[Channel]:
        return self._tools.get_channels(**_get_locals_without_self(locals()),
                                        session_key=self.WebSocketClient.session_key)

    def get_members(self, channel_url: str, next_token: str = None, limit: int = 20,
                    order: str = "member_nickname_alphabetical", member_state_filter: str = "all"):
        return self._tools.get_members(**_get_locals_without_self(locals()),
                                       session_key=self.WebSocketClient.session_key)

    def get_current_channels(self) -> List[Channel]:
        return self.WebSocketClient.current_channels

    def get_older_messages(self, channel_url: str, message_ts: int = 9007199254740991, prev_limit: int = 40,
                           next_limit: int = 0, reverse: bool = True) -> List[Message]:
        return self._tools.get_older_messages(**_get_locals_without_self(locals()),
                                              session_key=self.WebSocketClient.session_key)

    def create_channel(self, nicknames: List[str], group_name: str) -> Channel:
        channel = self._tools.create_channel(**_get_locals_without_self(locals()),
                                             own_name=self.WebSocketClient.own_name)
        self.WebSocketClient.add_channelid_sub_pair(channel)
        return channel

    def create_direct_channel(self, nickname: str) -> Channel:
        channel = self._tools.create_channel(nicknames=[nickname], group_name="",
                                             own_name=self.WebSocketClient.own_name)
        self.WebSocketClient.add_channelid_sub_pair(channel)
        return channel

    def accept_chat_invite(self, channel_url: str) -> None:
        self._tools.accept_chat_invite(channel_url, session_key=self.WebSocketClient.session_key)
        self.WebSocketClient.update_channelid_sub_pair()

    def rename_channel(self, name: str, channel_url: str) -> Channel:
        channel = self._tools.rename_channel(**_get_locals_without_self(locals()),
                                             session_key=self.WebSocketClient.session_key)
        self.WebSocketClient.update_channelid_sub_pair()
        return channel

    def hide_chat(self, user_id: str, channel_url: str, hide_previous_messages: bool = False,
                  allow_auto_unhide: bool = True) -> None:
        self._tools.hide_chat(**_get_locals_without_self(locals()), session_key=self.WebSocketClient.session_key)

    def enable_rate_limiter(self, max_calls: float, period: float) -> None:
        self.WebSocketClient.RateLimiter.is_enabled = True
        self.WebSocketClient.RateLimiter.max_calls = max_calls
        self.WebSocketClient.RateLimiter.period = period

    def disable_rate_limiter(self) -> None:
        self.WebSocketClient.RateLimiter.is_enabled = False

    def _load_session(self, pkl_name, force_reauth=False):
        def get_store_file_handle(pkl_name_, mode_):
            try:
                return open(f"{pkl_name_}-stored.pkl", mode_)
            except FileNotFoundError:
                return None

        session_store_f = None if force_reauth else get_store_file_handle(pkl_name, 'rb')

        if session_store_f is None or force_reauth:
            session_store_f = get_store_file_handle(pkl_name, 'wb+')
            self._r_authentication.authenticate()
            pickle.dump(self._r_authentication, session_store_f)
        else:
            try:
                self._r_authentication = pickle.load(session_store_f)
            except EOFError:
                return self._load_session(pkl_name, force_reauth=True)
        session_store_f.close()

        return self._r_authentication.sb_access_token, self._r_authentication.user_id
