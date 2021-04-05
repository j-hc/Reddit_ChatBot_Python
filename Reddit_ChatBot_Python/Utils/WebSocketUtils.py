from urllib.parse import urlencode
from .CONST import SB_User_Agent, SB_ai


def get_ws_url(user_id, access_token):
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


def get_current_channels(channels: list, user_id: str):
    channelid_sub_pairs = {}
    for channel in channels:
        room_name = None
        if channel.custom_type == "direct":
            for member in channel.members:
                if member.user_id != user_id:
                    room_name = member.nickname
                    break
        else:
            room_name = channel.channel.name
        channelid_sub_pairs.update({channel.channel.channel_url: room_name})
    return channelid_sub_pairs
