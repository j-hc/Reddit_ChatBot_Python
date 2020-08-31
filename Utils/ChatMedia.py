import requests


class ChatMedia:
    def __init__(self, ai, key, reddit_api_token):
        self.reddit_api_token = reddit_api_token
        self.headers = {
            'Accept': 'application/json',
            'User-Agent': 'Jand/3.0.82',
            'SendBird': f'Android,29,3.0.82,{ai}',
            'Session-Key': key,
            'Content-Type': 'application/json; charset=utf-8',
            'Host': 'sendbirdproxy.chat.redditmedia.com',
        }

    def delete_mesg(self, channel_url, mesg_id):
        uri = f'https://sendbirdproxy.chat.redditmedia.com/v3/group_channels/{channel_url}/messages/{mesg_id}'
        response = requests.delete(uri, headers=self.headers, data='{}').json()
        if response.get('error'):
            return False
        else:
            return True

    def fetch_older_msgs(self, channel_url, prev_limit, message_ts):
        params = {
            'is_sdk': 'true',
            'prev_limit': prev_limit,
            'next_limit': '0',
            'include': 'false',
            'reverse': 'true',
            'with_sorted_meta_array': 'false',
            'include_reactions': 'false',
            'message_ts': message_ts,
            'include_thread_info': 'false',
            'include_replies': 'false',
            'include_parent_message_text': 'false',
        }
        uri = f'https://sendbirdproxy.chat.redditmedia.com/v3/group_channels/{channel_url}/messages'
        response = requests.get(uri, headers=self.headers, params=params)

        return response.json()  # just return whole thing for now
