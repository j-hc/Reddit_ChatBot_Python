from typing import Callable, Optional
from ._utils.frame_model import FrameType, FrameModel

_hook = Callable[[FrameModel], Optional[bool]]


class Events:
    def __init__(self, ws_client):
        self.__WebSocketClient = ws_client
        self.__ready_executed = False

    def on_any(self, func: _hook = None, frame_type: FrameType = FrameType.MESG, run_parallel=False):
        def hook(resp: FrameModel):
            if resp.type_f == frame_type:
                return func(resp)
        if run_parallel:
            self.__WebSocketClient.parralel_hooks.append(hook)
        else:
            self.__WebSocketClient.after_message_hooks.append(hook)

    def on_reaction(self, func: _hook = None, run_parralel=False):
        def wrap(func):
            return self.on_any(func, FrameType.MRCT, run_parralel)

        if func is None:
            return wrap

        return wrap(func)

    def on_broadcast(self, func: _hook = None, run_parralel=False):
        def wrap(func):
            return self.on_any(func, FrameType.BRDM, run_parralel)

        if func is None:
            return wrap

        return wrap(func)

    def on_message(self, func: _hook = None, run_parallel=False):
        def wrap(func):
            return self.on_any(func, FrameType.MESG, run_parallel)

        if func is None:
            return wrap

        return wrap(func)

    def on_ready(self, func: _hook = None):
        def wrap(func):
            def hook(resp: FrameModel) -> Optional[bool]:
                try:
                    _ = resp.error
                    return
                except AttributeError:
                    pass
                if self.__ready_executed:
                    return
                else:
                    self.__ready_executed = True
                return func(resp)

            return self.on_any(hook, FrameType.LOGI, False)

        if func is None:
            return wrap

        return wrap(func)

    def on_user_read(self, func: _hook = None, run_parallel=False):
        def wrap(func):
            return self.on_any(func, FrameType.READ, run_parallel)

        if func is None:
            return wrap

        return wrap(func)

    def on_invitation(self, func: _hook = None, run_parallel=False):
        def wrap(func):
            def hook(resp: FrameModel) -> Optional[bool]:
                try:
                    _ = resp.data.inviter
                    invte = [invitee.nickname for invitee in resp.data.invitees]
                except AttributeError:
                    return
                if not (len(invte) == 1 and invte[0] == self.__WebSocketClient.own_name):
                    return
                return func(resp)

            return self.on_any(hook, FrameType.SYEV, run_parallel)

        if func is None:
            return wrap

        return wrap(func)

    def on_message_deleted(self, func: _hook = None, run_parallel=False):
        def wrap(func):
            return self.on_any(func, FrameType.DELM, run_parallel)

        if func is None:
            return wrap

        return wrap(func)

    def on_user_joined(self, func: _hook = None, run_parallel=False):
        def wrap(func):
            def hook(resp: FrameModel) -> Optional[bool]:
                try:
                    _ = resp.data.users[0].nickname
                    _ = resp.data.users[0].inviter.nickname
                except (AttributeError, IndexError):
                    return
                return func(resp)

            return self.on_any(hook, FrameType.SYEV, run_parallel)

        if func is None:
            return wrap

        return wrap(func)

    def on_user_left(self, func: _hook = None, run_parallel=False):
        def wrap(func):
            def hook(resp: FrameModel) -> Optional[bool]:
                try:
                    _ = resp.channel.disappearing_message
                    _ = resp.data.nickname
                except AttributeError:
                    return
                return func(resp)

            return self.on_any(hook, FrameType.SYEV, run_parallel)

        if func is None:
            return wrap

        return wrap(func)

    def on_user_typing(self, func: _hook = None, run_parallel=False):
        def wrap(func):
            def hook(resp: FrameModel) -> Optional[bool]:
                try:
                    _ = resp.data.nickname
                except AttributeError:
                    return
                if resp.cat != 10900:
                    return
                return func(resp)

            return self.on_any(hook, FrameType.SYEV, run_parallel)

        if func is None:
            return wrap

        return wrap(func)
