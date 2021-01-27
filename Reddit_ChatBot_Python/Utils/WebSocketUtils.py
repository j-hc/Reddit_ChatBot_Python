from urllib.parse import urlencode
import requests


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
        'show_empty': 'true',
        'custom_types': 'direct, group'
    }

    response = requests.get(f'https://sendbirdproxy.chat.redditmedia.com/v3/users/{user_id}/my_group_channels',
                            headers=headers, params=params).json()
    channelid_sub_pairs = {}
    for channel in response.get('channels', {}):
        channelid_sub_pairs.update({channel['channel']['channel_url']: channel['channel']['name']})
    return channelid_sub_pairs
