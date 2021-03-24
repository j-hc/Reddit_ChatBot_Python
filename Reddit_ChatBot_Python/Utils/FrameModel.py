import json
from types import SimpleNamespace


class FrameModel(SimpleNamespace):
    def __repr__(self):
        keys = sorted(self.__dict__)
        items = ("{}={!r}".format(k, self.__dict__[k]) for k in keys)
        return "({})".format(", ".join(items))


def convert_to_framemodel(d):
    return json.loads(d, object_hook=lambda d: FrameModel(**d))


def get_frame_data(data):
    data_r = data[4:]
    data_j = convert_to_framemodel(data_r)
    type_f = data[:4]

    # some presets
    if type_f == "MESG" and data_j.message == "":
        wfdata = convert_to_framemodel(data_j.data)
        data_j.message = wfdata.v1.snoomoji
    data_j.type_f = type_f

    return data_j
