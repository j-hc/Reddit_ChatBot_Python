from .Utils.WebSockClient import WebSockClient
from .Utils.ChatMedia import ChatMedia


class ChatBot:
    def __init__(self, ai, key, with_chat_media=False, **kwargs):
        self.WebSocketClient = WebSockClient(ai=ai, key=key, **kwargs)
        if with_chat_media:
            self.ChatMedia = ChatMedia(ai=ai, key=key)
