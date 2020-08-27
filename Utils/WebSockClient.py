import websocket
import time
from .FrameModel.FrameModel import FrameModel


class WebSockClient:
    def __init__(self, key, ai, user_id, enable_trace=False, channelid_sub_pairs=None, print_chat=True):
        if channelid_sub_pairs is None:
            self.channelid_sub_pairs = {}
        else:
            self.channelid_sub_pairs = channelid_sub_pairs

        websocket.enableTrace(enable_trace)
        uri = "wss://sendbirdproxy.chat.redditmedia.com" \
              f"/?p=_&pv=29&sv=3.0.82&ai={ai}&user_id={user_id}&access_token={key}"

        self.ws = websocket.WebSocketApp(uri,
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
        self._first = True

        self._after_message_hooks = []

    def on_open(self, ws):
        print("### successfully connected to the websocket ###")

    def add_after_message_hook(self, func):
        self._after_message_hooks.append(func)

    def set_respond_hook(self, input_, response, limited_to_users=None, lower_the_input=False, exclude_itself=True,
                         must_be_equal=True, quote_parent=False):

        if limited_to_users is not None and type(limited_to_users) == str:
            limited_to_users = [limited_to_users]

        def respond(resp):
            if resp.type_f == "MESG":
                sent_message = resp.message.lower() if lower_the_input else resp.message
                if (limited_to_users is None or resp.user_name in limited_to_users) and (exclude_itself and resp.user_name != self.own_name):
                    if (must_be_equal and sent_message == input_) or (not must_be_equal and input_ in sent_message):
                        if quote_parent:
                            response_prepped = f'@{resp.user_name}, {response}'
                        else:
                            response_prepped = response
                        self.send_message(response_prepped, resp.channel_url)
                        return True

        self.add_after_message_hook(respond)

    def run_4ever(self, ping_interval=15, ping_timeout=5):
        self.ws.run_forever(ping_interval=ping_interval, ping_timeout=ping_timeout)

    def print_chat_(self, resp):
        if resp.type_f == "MESG":
            print(f"{resp.user_name}@{self.channelid_sub_pairs.get(resp.channel_url)}: {resp.message}")

    def on_message(self, ws, message):
        resp = FrameModel(message)

        if self.print_chat:
            self.print_chat_(resp)

        if self._first:
            print(message)
            self.own_name = resp.nickname
            self._first = False
            if not resp.is_error:
                print('Everything is: OK')
        # else:
        #     print(resp_type, end='')
        #     print(message)

        for func in self._after_message_hooks:
            if func(resp):
                break

    def send_message(self, text, channel_url):
        payload = f'MESG{{"channel_url":"{channel_url}","message":"{text}","data":"{{\\"v1\\":{{\\"preview_collapsed\\":false,\\"embed_data\\":{{}},\\"hidden\\":false,\\"highlights\\":[],\\"message_body\\":\\"{text}\\"}}}}","mention_type":"users","req_id":"{self.req_id}"}}\n'
        self.ws.send(payload)
        self.req_id += 1

    def send_snoomoji(self, snoomoji, channel_url):
        payload = f'MESG{{"channel_url":"{channel_url}","message":"","data":"{{\\"v1\\":{{\\"preview_collapsed\\":false,\\"embed_data\\":{{\\"site_name\\":\\"Reddit\\"}},\\"hidden\\":false,\\"snoomoji\\":\\"{snoomoji}\\"}}}}","mention_type":"users","req_id":"{self.req_id}"}}\n'
        self.ws.send(payload)
        self.req_id += 1

    def on_error(self, ws, error):
        print(error)

    def on_close(self, ws):
        print("### websock closed ###")

    # def on_ping(self, ws, r):
    #     print("ping")
    #
    # def on_pong(self, ws, r):
    #     print("pong")
