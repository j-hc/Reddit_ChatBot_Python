import json
from types import SimpleNamespace


class FrameModel:
    @staticmethod
    def get_frame_data(data):
        data_r = data[4:]
        data_j = json.loads(data_r, object_hook=lambda d: SimpleNamespace(**d))
        type_f = data[:4]

        # some presets
        if type_f == "MESG" and data_j.message == "":
            wfdata = json.loads(data_j.data, object_hook=lambda d: SimpleNamespace(**d))
            data_j.message = wfdata.v1.snoomoji
        data_j.type_f = type_f

        return data_j
