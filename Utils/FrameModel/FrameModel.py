import json


class FrameModel:
    def __init__(self, data):
        first_curly = data.find('{')
        self.type_f = data[:first_curly]
        data_r = data[first_curly:]
        data_j = json.loads(data_r)

        if self.type_f == "LOGI":
            self.key = data_j['key']
            self.ekey = data_j['ekey']
            self.pong_timeout = data_j['pong_timeout']
            self.login_ts = data_j['login_ts']
            self.unread_cnt = data_j['unread_cnt']
            self.user_id = data_j['user_id']
            self.nickname = data_j['nickname']
        elif self.type_f == "MESG":
            self.unread_cnt = data_j['unread_cnt']
            self.msg_id = data_j['msg_id']
            self.is_op_msg = data_j['is_op_msg']
            self.is_guest_msg = data_j['is_guest_msg']
            self.message = data_j['message']
            self.ts = data_j['ts']
            self.channel_url = data_j['channel_url']
            self.user_name = data_j['user']['name']
            self.user_guest_id = data_j['user']['guest_id']
            self.mentioned_users = data_j['mentioned_users']
        else:
            pass

    def __repr__(self):
        return f"Frame: ({self.type_f})"
