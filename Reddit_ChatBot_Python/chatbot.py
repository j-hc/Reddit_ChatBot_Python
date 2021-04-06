from .ws_client import WebSockClient
import pickle
from .reddit_auth import _RedditAuthBase, TokenAuth, PasswordAuth
from websocket import WebSocketConnectionClosedException
from ._api.tools import Tools
from typing import Dict, List, Callable, Optional
from ._utils.frame_model import FrameType, FrameModel

_hook = Callable[[FrameModel], Optional[bool]]


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

        self.WebSocketClient = WebSockClient(access_token=sb_access_token, user_id=user_id, **kwargs)
        self._tools = Tools(self._r_authentication)
        self.WebSocketClient._get_current_channels = self._tools.get_channels

    def get_chatroom_name_id_pairs(self) -> Dict[str, str]:
        return self.WebSocketClient.channelid_sub_pairs

    def on_message_hook(self, func: _hook) -> None:
        self.on_frame_hook(frame_type=FrameType.MESG)(func)

    def on_ready_hook(self, func: _hook) -> None:
        self.on_frame_hook(frame_type=FrameType.LOGI)(func)

    def on_frame_hook(self, frame_type: FrameType = FrameType.MESG) -> Callable[[_hook], None]:
        def on_frame_hook_append(func: _hook):
            def hook(resp: FrameModel):
                if resp.type_f == frame_type:
                    func(resp)
            self.WebSocketClient.after_message_hooks.append(hook)
        return on_frame_hook_append

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

        self.on_frame_hook(frame_type=FrameType.MESG)(hook)

    def on_invitation_hook(self, func: _hook) -> None:
        def hook(resp: FrameModel) -> Optional[bool]:
            try:
                _ = resp.data.inviter
                invte = [invitee.nickname for invitee in resp.data.invitees]
            except AttributeError:
                return
            if not (len(invte) == 1 and invte[0] == self.WebSocketClient.own_name):
                return
            func(resp)

        self.on_frame_hook(frame_type=FrameType.SYEV)(hook)

    def on_message_deleted_hook(self, func: _hook) -> None:
        self.on_frame_hook(frame_type=FrameType.DELM)(func)

    def on_user_joined_hook(self, func: _hook):
        def hook(resp: FrameModel) -> Optional[bool]:
            try:
                _ = resp.data.users[0].nickname
                _ = resp.data.users[0].inviter.nickname
            except (AttributeError, IndexError):
                return
            func(resp)
        self.on_frame_hook(FrameType.SYEV)(hook)

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

        self.on_user_joined_hook(hook)

    def on_user_left_hook(self, func: _hook) -> None:
        def hook(resp: FrameModel) -> Optional[bool]:
            try:
                _ = resp.channel.disappearing_message
                _ = resp.data.nickname
            except AttributeError:
                return
            func(resp)
        self.on_frame_hook(FrameType.SYEV)(hook)

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

        self.on_user_left_hook(hook)

    def send_message(self, text: str, channel_url: str) -> None:
        self.WebSocketClient.ws_send_message(text, channel_url)

    def send_snoomoji(self, snoomoji: str, channel_url: str) -> None:
        self.WebSocketClient.ws_send_snoomoji(snoomoji, channel_url)

    def send_typing_indicator(self, channel_url: str) -> None:
        self.WebSocketClient.ws_send_typing_indicator(channel_url)

    def stop_typing_indicator(self, channel_url: str) -> None:
        self.WebSocketClient.ws_stop_typing_indicator(channel_url)

    def run_4ever(self, auto_reconnect: bool = True, max_retries: int = 500, skip_utf8_validation=True) -> None:
        for _ in range(max_retries):
            self.WebSocketClient.ws_run_forever(skip_utf8_validation=skip_utf8_validation)
            if self.WebSocketClient.is_logi_err and isinstance(self._r_authentication, PasswordAuth):
                self.WebSocketClient.logger.info('Re-Authenticating...')
                if self._store_session:
                    sb_access_token, _ = self._load_session(self._r_authentication.reddit_username, force_reauth=True)
                else:
                    sb_access_token = self._r_authentication.authenticate()['sb_access_token']
                self.WebSocketClient.update_ws_app_urls_access_token(sb_access_token)
            elif not (auto_reconnect and isinstance(self.WebSocketClient.last_err, WebSocketConnectionClosedException)):
                break
            self.WebSocketClient.logger.info('Auto Reconnecting...')

    def kick_user(self, channel_url: str, user_id: str, duration: int) -> None:
        self._tools.kick_user(channel_url, user_id, duration)

    def delete_mesg(self, channel_url: str, msg_id: str) -> None:
        self._tools.delete_message(channel_url, msg_id, session_key=self.WebSocketClient.session_key)

    def invite_user_to_channel(self, channel_url: str, nicknames: List[str]) -> None:
        self._tools.invite_user(channel_url, nicknames)

    def get_chat_invites(self) -> list:
        return self._tools.get_channels(session_key=self.WebSocketClient.session_key,
                                        member_state_filter="invited_only")

    def get_channels(self, **kwargs) -> list:
        return self._tools.get_channels(session_key=self.WebSocketClient.session_key, **kwargs)

    def get_older_messages(self, channel_url, prev_limit, next_limit, reverse, message_ts) -> FrameType:
        return self._tools.get_older_messages(channel_url, prev_limit, next_limit, reverse, message_ts,
                                              session_key=self.WebSocketClient.session_key)

    def create_channel(self, nicknames: List[str], group_name: str):
        channel = self._tools.create_channel(nicknames, group_name, own_name=self.WebSocketClient.own_name)
        self.WebSocketClient.update_channelid_sub_pair()
        return channel

    def accept_chat_invite(self, channel_url: str) -> None:
        self._tools.accept_chat_invite(channel_url, session_key=self.WebSocketClient.session_key)
        self.WebSocketClient.update_channelid_sub_pair()

    def hide_chat(self, user_id: str, channel_url: str, hide_previous_messages: bool = False,
                  allow_auto_unhide: bool = True) -> None:
        self._tools.hide_chat(user_id, channel_url, hide_previous_messages, allow_auto_unhide,
                              session_key=self.WebSocketClient.session_key)

    def enable_rate_limiter(self, max_calls: float, period: float) -> None:
        self.WebSocketClient.RateLimiter.is_enabled = True
        self.WebSocketClient.RateLimiter.max_calls = max_calls
        self.WebSocketClient.RateLimiter.period = period

    def disable_rate_limiter(self) -> None:
        self.WebSocketClient.RateLimiter.is_enabled = False

    def _load_session(self, pkl_name, force_reauth=False):
        def get_store_file_handle(pkl_name_, mode_):
            try:
                return open(f'{pkl_name_}-stored.pkl', mode_)
            except FileNotFoundError:
                return None

        session_store_f = None if force_reauth else get_store_file_handle(pkl_name, 'rb')

        if session_store_f is None or force_reauth:
            session_store_f = get_store_file_handle(pkl_name, 'wb+')
            self._r_authentication.authenticate()
            pickle.dump(self._r_authentication, session_store_f)
        else:
            self._r_authentication = pickle.load(session_store_f)
        session_store_f.close()

        return self._r_authentication.sb_access_token, self._r_authentication.user_id