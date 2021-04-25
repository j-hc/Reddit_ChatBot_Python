from urllib.parse import urlencode
from .consts import SB_User_Agent, SB_ai
from .._api.models import Channel
from typing import List


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
        if chn_name == "":
            for mmbr in channel.members:
                if mmbr.user_id != own_user_id:
                    chn_name = mmbr.nickname
                    break
        channelid_sub_pairs.update({channel.channel_url: chn_name})
    return channelid_sub_pairs
