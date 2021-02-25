Reddit ChatRoom
---------------

a fully functional (almost) bot library for reddit chatrooms!

no selenium no bullsh*t, just directly websocket

works either with reddit username & password or the api token (not a regular one you get from your registered app)

re-authentication prior to auto reconnect is only possible with PasswordAuth


Installation
------------

    pip3 install Reddit-ChatBot-Python

required:

    python<=3.8.7

packages:

    websocket_client
    requests
    numpy
    wsaccel

wsaccel and numpy are for extra performance in websocket operations


Example
-------

```python
from Reddit_ChatBot_Python import ChatBot, RedditAuthentication
import random  # for a basic dice rolling game

# create authentication with username and pass
reddit_authentication = RedditAuthentication.PasswordAuth(reddit_username="", reddit_password="", twofa="")  # 2FA supported although not necessary obv..

# instantiate the chatbot
chatbot = ChatBot(print_chat=True, store_session=True, print_websocket_frames=False,  # some parameters u might wanna know
                  authentication=reddit_authentication)

# you can add a rate limit like so:
chatbot.enable_rate_limiter(max_calls=23, # how many messages will be sent by the bot
                            period=1.5  # in what period (minutes)
                            )

# now you can add hooks which will be executed when a frame is received like so:
@chatbot.after_message_hook() # default frame_type is MESG
def dice_roller(resp):  # resp is a SimpleNamespace that carries all the data of the received frame
    messg_s = resp.message.split()
    if messg_s[0] == "!roll" and len(messg_s) == 3:  # if received message says !roll
        limit_bottom = int(messg_s[1])
        limit_top = int(messg_s[2])

        rolled_number = random.randint(limit_bottom, limit_top)
        response_text = f"@{resp.user.name} {rolled_number}. Better luck next time!"
        # a basic roll game

        # send typing indicator cuz why not? maybe they think you are a real person
        chatbot.send_typing_indicator(resp.channel_url)
        chatbot.send_message(response_text, resp.channel_url)  # and send the message, always add resp.channel_url as the second argument
        chatbot.send_snoomoji('partyparrot', resp.channel_url)  # and send a snoomoji cuz why not??
        return True  # return true if you want to be done with checking the other hooks, otherwise return None or False
        # keep in mind that first added hooks gets executed first

# now everytime someone says "!roll 1 100", the bot will roll a dice between 1 and 100 and send the result!

@chatbot.after_message_hook()
def keeper_of_decency(resp): # WE WILL KEEP THE DECENCY IN THE CHAT BOIS
    if resp.message == "*some very bad slur word*":
        chatbot.kick_user(channel_url=resp.channel_url, user_id=resp.user.guest_id, duration=600) # duration is in secs
        chatbot.send_message(f'i banned {resp.user.name} for 10 mins', resp.channel_url)
        return True
    elif resp.message == "*another bad word*":
        chatbot.delete_mesg(channel_url=resp.channel_url, msg_id=resp.msg_id)
        chatbot.send_message(f"i deleted {resp.user.name}'s message", resp.channel_url)
        return True


# or you can add a basic response hook directly like so:
chatbot.set_respond_hook(input_="Hi", response="Hello {nickname}! sup?", limited_to_users=None, lower_the_input=False,
                         exclude_itself=True, must_be_equal=True, limited_to_channels=["my cozy chat group"]) # you can limit by indicating chatroom's name

# you can add a welcome message for newly joined users:
chatbot.set_welcome_message("welcome to the my cozy chat group u/{nickname}!)", limited_to_channels=["my cozy chat group"])

# and a farewell message too:
chatbot.set_farewell_message("Too bad u/{nickname} left us :(", limited_to_channels=["my cozy chat group"])

# there is also another hook type for invitation frames
@chatbot.on_invitation_hook
def on_invit(resp):
    if resp.channel_type == "group":
        invit_type = "group chat"
    elif resp.channel_type == "direct":
        invit_type = "DM"
    else:
        invit_type = None
    print(f"got invited to {invit_type} by {resp.data.inviter.nickname}")
    chatbot.accept_chat_invite(resp.channel_url)
    chatbot.send_message("Hello! I accepted your invite", resp.channel_url)


# and finally, run forever...
chatbot.run_4ever(auto_reconnect=True)  # set auto_reconnect so as to re-connect in case remote server shuts down the connection after some period of time
```

Instances of Frames
------------------

You access stuff like this with dot operator:

    message = resp.message
    nickname = resp.user.name

<details>
  <summary>Instance of MESG Frame (regular chat message)</summary>
  
```json
{
  "msg_id": 1000000,
  "is_op_msg": false,
  "is_guest_msg": true,
  "message": "msg",
  "silent": false,
  "ts": 1611782454265,
  "channel_url": "sendbird_group_channel_000000000_0000000000000000000000000000000000000000",
  "is_removed": false,
  "sts": 1611782454265,
  "user": {
    "is_blocked_by_me": false,
    "require_auth_for_profile_image": false,
    "name": "*user nickname*",
    "is_bot": false,
    "image": "",
    "is_active": true,
    "guest_id": "t2_5z9rqylm",
    "friend_discovery_key": null,
    "role": "",
    "friend_name": null,
    "id": 10000,
  },
}
```
</details>


<details>
  <summary>Instance of Invitation Frame</summary>
  
```json
{
  "unread_cnt": {
    "all": 1,
    "ts": 1614006345986
  },
  "is_super": false,
  "data": {
    "inviter": {
      "nickname": "*inviter nickname*",
      "metadata": {
      },
      "require_auth_for_profile_image": false,
      "profile_url": "",
      "user_id": "*user id str t2_ included*"
    },
    "invited_at": 1614006345956,
    "invitees": [
      {
        "nickname": "*bot's nickname*",
        "metadata": {
        },
        "require_auth_for_profile_image": false,
        "profile_url": "",
        "user_id": "t2_5z9rqylm"
      }
    ]
  },
  "ts": 1614006345978,
  "is_access_code_required": false,
  "cat": 10020,
  "channel_type": "*can either be 'group' for group chat or 'direct' for DM*",
  "channel_id": 177639012,
  "sts": 1614006345978,
  "channel_url": "sendbird_group_channel_000000000_0000000000000000000000000000000000000000"
}
```
</details>


<details>
  <summary>Instance of User Joined Frame</summary>
  
```json
{
  "is_super": false,
  "data": {
    "is_bulk": true,
    "users": [
      {
        "require_auth_for_profile_image": false,
        "nickname": "nickname",
        "role": "",
        "user_id": "t2_5z9rqylm",
        "inviter": {
          "user_id": "t2_5z9rqylm",
          "role": "",
          "require_auth_for_profile_image": false,
          "nickname": "nickname",
          "profile_url": "",
          "metadata": {
          }
        },
        "profile_url": "",
        "metadata": {
        }
      }
    ]
  },
  "ts": 1614264797294,
  "is_access_code_required": false,
  "cat": 10000,
  "channel_type": "group",
  "channel_id": 177639012,
  "sts": 1614264797294,
  "channel_url": "sendbird_group_channel_000000000_0000000000000000000000000000000000000000"
}
```
</details>


<details>
  <summary>Instance of User Left Frame</summary>
  
```json
{
  "channel_type": "group",
  "channel_id": 177639012,
  "is_super": false,
  "channel": {
    "custom_type": "group",
    "is_ephemeral": false,
    "freeze": false,
    "disappearing_message": {
      "message_survival_seconds": -1,
      "is_triggered_by_message_read": false
    },
    "member_count": 2,
    "is_broadcast": false,
    "last_message": null,
    "unread_mention_count": 0,
    "sms_fallback": {
      "wait_seconds": -1,
      "exclude_user_ids": [
      ]
    },
    "is_discoverable": false,
    "ignore_profanity_filter": false,
    "channel_url": "sendbird_group_channel_000000000_0000000000000000000000000000000000000000",
    "message_survival_seconds": -1,
    "unread_message_count": 0,
    "is_distinct": false,
    "cover_url": "https:\/\/static.sendbird.com\/sample\/cover\/cover_00.jpg",
    "members": [
      {
        "is_active": true,
        "state": "",
        "user_id": 10000000,
        "is_online": false,
        "is_muted": false,
        "require_auth_for_profile_image": false,
        "last_seen_at": 0,
        "nickname": "nickname1",
        "profile_url": "",
        "metadata": {
        }
      },
      {
        "is_active": true,
        "state": "",
        "user_id": 10000000,
        "is_online": false,
        "is_muted": false,
        "require_auth_for_profile_image": false,
        "last_seen_at": 0,
        "nickname": "nickname2",
        "profile_url": "",
        "metadata": {
        }
      }
    ],
    "is_public": false,
    "data": "",
    "joined_member_count": 1,
    "is_super": false,
    "name": "group name",
    "created_at": 1614264775,
    "is_access_code_required": false,
    "max_length_message": 5000
  },
  "sts": 1614265517558,
  "channel_url": "sendbird_group_channel_000000000_0000000000000000000000000000000000000000",
  "data": {
    "require_auth_for_profile_image": false,
    "member_count": 2,
    "user_id": "t2_5z9rqylm",
    "joined_member_count": 1,
    "nickname": "nickanme of user who left the group",
    "profile_url": "",
    "metadata": {
      
    }
  },
  "ts": 1614265517558,
  "is_access_code_required": false,
  "cat": 10001
}
```
</details>



Showcase of some other fun stuff you can do with this..
-------------------------------------------------------

**Save chatroom messages to a text file (or even in an sql database or some other sht)**

```python
messages_f_handle = open('reddit-chat-msgs.txt', 'w')

@chatbot.after_message_hook(frame_type='MESG')
def save_chat_messages_into_a_txt_file(resp):
    chatroom_name_id_pairs = chatbot.get_chatroom_name_id_pairs()
    message = resp.message
    nickname = resp.user.name
    chatroom_name = chatroom_name_id_pairs.get(resp.channel_url)
    formatted_msg = f"{nickname} said {message} in {chatroom_name}"
    messages_f_handle.write(formatted_msg)
    messages_f_handle.flush()
```

**Catch deleted messages**

```python
@chatbot.after_message_hook(frame_type='DELM')
def catch_deleted_messages(resp):
    caught_deleted_message_id = resp.msg_id
```

**See who invited who**

```python
@chatbot.after_message_hook(frame_type='SYEV')
def catch_invitees_and_inviters(resp):
    try:
        inviter = resp.data.inviter.nickname
        invitees = [invitee.nickname for invitee in resp.data.invitees]
    except AttributeError:
        return
```