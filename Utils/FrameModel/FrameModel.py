import json
from collections import namedtuple
from collections.abc import Mapping


class FrameModel:
    """
    mostly important fields of MESG:
    msg_id
    is_op_msg
    is_guest_msg
    message
    ts
    channel_url
    user -> name, guest_id, is_blocked_by_me
    mentioned_users
    """

    @staticmethod
    def get_frame_data(data):
        first_curly = data.find('{')
        data_r = data[first_curly:]
        data_j = json.loads(data_r)
        type_f = data[:first_curly]

        # some presets
        if data_j.get('error') is None:
            data_j['error'] = False
        if data_j.get('message') == "":
            data_j['message'] = "[snoomoji]"

        data_j['type_f'] = type_f
        return FrameModel._mapping_to_named_tuple(data_j)

    @staticmethod
    def _mapping_to_named_tuple(mapping, name="framedata"):
        if isinstance(mapping, Mapping):
            mapping = {key: FrameModel._mapping_to_named_tuple(value, key) for key, value in mapping.items()}
            return namedtuple(name, mapping.keys())(**mapping)
        elif isinstance(mapping, list):
            return tuple([FrameModel._mapping_to_named_tuple(item, name) for item in mapping])
        else:
            return mapping
