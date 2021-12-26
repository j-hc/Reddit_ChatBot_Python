from urllib.parse import urlencode
from .consts import SB_User_Agent, SB_ai
from .._api.models import Channel, CustomType
from typing import List
import logging


def get_ws_url(user_id: str, access_token: str):
    socket_base = "wss://sendbirdproxyk8s.chat.redditmedia.com"
    ws_params = {
        "user_id": user_id,
        "access_token": access_token,
        "p": "Android",
        "pv": 30,
        "sv": "3.0.144",
        "ai": SB_ai,
        "SB-User-Agent": SB_User_Agent,
        "active": "1"
    }
    return f"{socket_base}/?{urlencode(ws_params)}"


def pair_channel_and_names(channels: List[Channel], own_user_id: str):
    channelid_sub_pairs = {}
    for channel in channels:
        chn_name = channel.name
        if channel.custom_type == CustomType.direct:
            for mmbr in channel.members:
                if mmbr.user_id != own_user_id:
                    chn_name = mmbr.nickname
                    break
        channelid_sub_pairs.update({channel.channel_url: chn_name})
    return channelid_sub_pairs


def configure_loggers():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    sh = logging.StreamHandler()
    sh.setLevel(logging.INFO)
    sh.setFormatter(logging.Formatter(fmt="%(asctime)s, %(levelname)s: %(message)s", datefmt="%H:%M"))
    ws_logger = logging.getLogger("websocket")
    ws_logger.propagate = False
    ws_logger.addHandler(sh)
    logger.addHandler(sh)
    return logger


def chat_printer(resp, channelid_sub_pairs):
    if resp.message == "":
        try:
            msg = resp.data.v1.snoomoji
        except AttributeError:
            msg = resp.message
    else:
        msg = resp.message
    print(f"{resp.user.name}@{channelid_sub_pairs.get(resp.channel_url)}: {msg}")
