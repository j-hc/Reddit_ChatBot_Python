import json


class FrameModel:
    def __init__(self, data):
        first_curly = data.find('{')
        self.type_f = data[:first_curly]
        data_r = data[first_curly:]
        data_j = json.loads(data_r)

        if self.type_f == "LOGI":
            self.key = data_j.get('key')
            self.ekey = data_j.get('ekey')
            self.pong_timeout = data_j.get('pong_timeout')
            self.login_ts = data_j.get('login_ts')
            self.unread_cnt = data_j.get('unread_cnt')
            self.user_id = data_j.get('user_id')
            self.nickname = data_j.get('nickname')
            self.is_error = data_j.get('error')
        elif self.type_f == "MESG":
            self.unread_cnt = data_j.get('unread_cnt')
            self.msg_id = data_j.get('msg_id')
            self.is_op_msg = data_j.get('is_op_msg')
            self.is_guest_msg = data_j.get('is_guest_msg')
            self.message = data_j.get('message')
            if self.message == "":
                self.message = "[snoomoji]"
            self.ts = data_j.get('ts')
            self.channel_url = data_j.get('channel_url')
            self.user_name = data_j.get('user').get('name')
            self.user_guest_id = data_j.get('user').get('guest_id')
            self.mentioned_users = data_j.get('mentioned_users')
        else:
            pass

    def __repr__(self):
        return f"Frame: ({self.type_f})"
