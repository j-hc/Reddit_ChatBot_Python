from urllib.parse import urlencode
import requests


class FrameSkeletons:
    MESG_regular = 'MESG{{"channel_url":"{channel_url}","message":"{text}","data":"{{\\"v1\\":{{\\"preview_collapsed\\":false,\\"embed_data\\":{{}},\\"hidden\\":false,\\"highlights\\":[],\\"message_body\\":\\"{text}\\"}}}}","mention_type":"users","req_id":"{req_id}"}}\n'
    MESG_snoo = 'MESG{{"channel_url":"{channel_url}","message":"","data":"{{\\"v1\\":{{\\"preview_collapsed\\":false,\\"embed_data\\":{{\\"site_name\\":\\"Reddit\\"}},\\"hidden\\":false,\\"snoomoji\\":\\"{snoomoji}\\"}}}}","mention_type":"users","req_id":"{req_id}"}}\n'
    TPST = 'TPST{{"channel_url":"{channel_url}","time":{time},"req_id":""}}\n'


def _get_ws_url(socket_base, params):
    return f"{socket_base}/?{urlencode(params)}"


def print_chat_(resp, channelid_sub_pairs):
    if resp.type_f == "MESG":
        print(f"{resp.user.name}@{channelid_sub_pairs.get(resp.channel_url)}: {resp.message}")


def _get_current_channels(user_id, logi_key):
    headers = {
        'session-key': logi_key,
        'SB-User-Agent': 'Android%2Fc3.0.144',
        'User-Agent': None
    }
    params = {
        'show_member': 'true',
        'show_frozen': 'true',
        'public_mode': 'all',
        'member_state_filter': 'joined_only',
        'super_mode': 'all',
        'limit': '40',
        'show_empty': 'true'
    }
    response = requests.get(f'https://sendbirdproxyk8s.chat.redditmedia.com/v3/users/{user_id}/my_group_channels',
                            headers=headers, params=params).json()
    channelid_sub_pairs = {}
    room_name = None
    for channel in response.get('channels', {}):
        if channel['custom_type'] == "direct":
            for member in channel['members']:
                if member['user_id'] != user_id:
                    room_name = member['nickname']
                    break
        else:
            room_name = channel['channel']['name']
        channelid_sub_pairs.update({channel['channel']['channel_url']: room_name})
    return channelid_sub_pairs
