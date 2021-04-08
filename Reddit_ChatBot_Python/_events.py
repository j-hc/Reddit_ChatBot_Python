from typing import Callable, Optional
from ._utils.frame_model import FrameType, FrameModel

_hook = Callable[[FrameModel], Optional[bool]]


class Events:
    def __init__(self, ws_client):
        self.WebSocketClient = ws_client

    def on_message(self, func: _hook) -> None:
        self.on_any(frame_type=FrameType.MESG)(func)

    def on_ready(self, func: _hook) -> None:
        self.on_any(frame_type=FrameType.LOGI)(func)

    def on_any(self, frame_type: FrameType = FrameType.MESG) -> Callable[[_hook], None]:
        def on_frame_hook_append(func: _hook):
            def hook(resp: FrameModel):
                if resp.type_f == frame_type:
                    func(resp)

            self.WebSocketClient.after_message_hooks.append(hook)

        return on_frame_hook_append

    def on_invitation(self, func: _hook) -> None:
        def hook(resp: FrameModel) -> Optional[bool]:
            try:
                _ = resp.data.inviter
                invte = [invitee.nickname for invitee in resp.data.invitees]
            except AttributeError:
                return
            if not (len(invte) == 1 and invte[0] == self.WebSocketClient.own_name):
                return
            func(resp)

        self.on_any(frame_type=FrameType.SYEV)(hook)

    def on_message_deleted(self, func: _hook) -> None:
        self.on_any(frame_type=FrameType.DELM)(func)

    def on_user_joined(self, func: _hook):
        def hook(resp: FrameModel) -> Optional[bool]:
            try:
                _ = resp.data.users[0].nickname
                _ = resp.data.users[0].inviter.nickname
            except (AttributeError, IndexError):
                return
            func(resp)
        self.on_any(FrameType.SYEV)(hook)

    def on_user_left(self, func: _hook) -> None:
        def hook(resp: FrameModel) -> Optional[bool]:
            try:
                _ = resp.channel.disappearing_message
                _ = resp.data.nickname
            except AttributeError:
                return
            func(resp)
        self.on_any(FrameType.SYEV)(hook)

    def on_user_typing(self, func: _hook) -> None:
        def hook(resp: FrameModel) -> Optional[bool]:
            try:
                _ = resp.data.nickname
                _ = resp.channel_url
            except AttributeError:
                return
            if resp.cat != 10900:
                return
            func(resp)
        self.on_any(FrameType.SYEV)(hook)
