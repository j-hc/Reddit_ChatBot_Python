Reddit ChatRoom
---------------

a fully featured, event-driven chatbot library for reddit chatrooms in python!

no selenium no bullsh*t, just directly websocket

works either with reddit username & password or the api token (not a regular one you get from your registered app as it's not fully scoped)

re-authentication prior to auto re-connect is only possible with PasswordAuth


Installation
------------

    pip install Reddit-ChatBot-Python

required:

    websocket_client
    requests
    dacite


There is a skip_utf8_validation parameter for run_4ever method which slows things down when set to False.
If you want to set it to False, it is recommended that you install with extra modules:

    pip3 install Reddit-ChatBot-Python[extra]


Usage
-------

The module is multi-threaded and event-driven. You handle what's gonna happen on these events
by writing your function with the specific event's decorator.

First of all, for creating an instance of RedditAuthenticaton, there are two options

Recommended way is to create a PasswordAuth:
```python
from Reddit_ChatBot_Python RedditAuthentication

reddit_authentication = RedditAuthentication.PasswordAuth(reddit_username="",
                                                          reddit_password="",
                                                          twofa="")
```

or you can go with your self-obtained api key. (not the one you get from your registered app)
```python
from Reddit_ChatBot_Python RedditAuthentication

reddit_authentication = RedditAuthentication.TokenAuth(token="")
```

---

then instantiating the chatbot with the reddit_authentication passed in
```python
from Reddit_ChatBot_Python ChatBot

chatbot = ChatBot(print_chat=True,
                  store_session=True,
                  log_websocket_frames=False,
                  authentication=reddit_authentication,
                  global_blacklist_user={"user1", "user2"},
                  global_blacklist_words={"badword1", "badword2"}
                  )
```
```print_chat``` is for ```print```ing the chat messages on console

```store_session``` when set to True, creates a pickle file storing reddit_authentication on
the same directory the main script was called in. Speeds up the websocket connection process but
not necessary.

```log_websocket_frames``` logs the non-parsed websocket frames on the console

```authentication``` is the ```RedditAuthentication``` you instantiated before

```global_blacklist_users``` is the ```set``` of users that events doesn't get executed on

```global_blacklist_words``` is the ```set``` of words(like n-word) that event doesn't get executed on

---

The events:
```python
@chatbot.event.on_message
```
The event of a receving a normal chat message.

```python
@chatbot.event.on_ready
```
The event of a connecting to the chats for the first time.

```python
@chatbot.event.on_invitation
```
The event of a receving a chat invitation whether direct or group.

```python
@chatbot.event.on_message_deleted
```
The event of a user deleting his/her message.

```python
@chatbot.event.on_user_joined
```
The event of a user joining to a chat the bot is in.

```python
@chatbot.event.on_user_left
```
The event of a user leaving a chat the bot is in.

---

All events receives a parsed frame as an argument. They are handled like this.:
```python
@chatbot.event.on_message
def greet(resp):
    if resp.user.name == "botsname":
        return True
    if resp.message == "Hi!":
        chatbot.send_message("Hello!", resp.channel_url)
        return True
```

- Returning ```True``` from events means that handling of the other events won't be carried out.

- ```resp.channel_url``` is the url of the channel we want to send the message to (resp.channel_url in this case
  which is the channel in which the "Hi!" message was sent.)
  
The argument ```resp``` carries more data than just the user and the message string. The Instances of resp for
all event are listed below.

---
Other parts of the API is also implemented:
```python
chatbot.delete_message(channel_url, msg_id)
chatbot.kick_user(channel_url, user_id, duration)
chatbot.invite_user(channel_url, nicknames)
chatbot.accept_chat_invite(channel_url)
chatbot.get_channels(limit, order, show_member, show_read_receipt, show_empty, member_state_filter,
                     super_mode,public_mode, unread_filter, hidden_mode, show_frozen)
chatbot.leave_chat(channel_url)
chatbot.create_channel(nicknames, group_name, own_name)
chatbot.hide_chat(user_id, channel_url, hide_previous_messages, allow_auto_unhide)
chatbot.get_older_messages(channel_url, prev_limit, next_limit, reverse)
```

---
All there is left is starting the chatbot:
```python
chatbot.run_4ever(auto_reconnect=True)
```

---

Instances of Frames ("resp" object of the events)
------------------

You access stuff like this with the dot operator:

    message = resp.message
    nickname = resp.user.name

<details>
  <summary>Instance of regular chat message Frame - event.on_message</summary>
  
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
    "id": 10000
  }
}
```
</details>


<details>
  <summary>Instance of Invitation Frame - event.on_invitation</summary>
  
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
  <summary>Instance of User Joined Frame - event.on_user_joined</summary>
  
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
  <summary>Instance of User Left Frame - event.on_user_left</summary>
  
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


<details>
  <summary>Instance of Deleted Message Frame - event.on_message_deleted</summary>
  
```json
{
  "is_super": false,
  "msg_id": 2323966291,
  "ts": 1614266924885,
  "channel_type": "group",
  "channel_id": 177623421,
  "sts": 1614266924885,
  "channel_url": "sendbird_group_channel_000000000_0000000000000000000000000000000000000000"
}
```
</details>

<details>
  <summary>Instance of User Typing Frame - event.on_user_typing</summary>
  
```json
{
  "is_super": false,
  "data": {
    "require_auth_for_profile_image": false,
    "user_id": "t2_xxxxxx",
    "nickname": "xxxx",
    "profile_url": "",
    "metadata": {
      
    }
  },
  "ts": 1617897296948,
  "is_access_code_required": false,
  "cat": 10900,
  "channel_type": "group",
  "channel_id": 11111111,
  "sts": 1617897296948,
  "channel_url": "sendbird_group_channel_000000000_0000000000000000000000000000000000000000"
}
```
</details>

Complete Example
-------

```python
from Reddit_ChatBot_Python import ChatBot, RedditAuthentication
import random  # for a basic dice rolling game

# create authentication with username and pass
reddit_authentication = RedditAuthentication.PasswordAuth(reddit_username="", reddit_password="",
                                                          twofa="")  # 2FA supported although not necessary obv..

# instantiate the chatbot
chatbot = ChatBot(print_chat=True, store_session=True, log_websocket_frames=False,  # some parameters u might wanna know
                  authentication=reddit_authentication)

# you can add a rate limit like so:
chatbot.enable_rate_limiter(max_calls=23,  # how many messages will be sent by the bot
                            period=1.5  # in what period (minutes)
                            )


# now you can add hooks which will be executed when a frame is received like so:
@chatbot.event.on_message
def dice_roller(resp):  # resp is a SimpleNamespace that carries all the data of the received frame
    messg_s = resp.message.split()
    if messg_s[0] == "!roll" and len(messg_s) == 3:  # if received message says !roll
        limit_bottom = int(messg_s[1])
        limit_top = int(messg_s[2])

        rolled_number = random.randint(limit_bottom, limit_top)
        response_text = f"@{resp.user.name} {rolled_number}. Better luck next time!"
        # a simple game

        # send typing indicator cuz why not? maybe they think you are a real person
        chatbot.send_typing_indicator(resp.channel_url)
        chatbot.send_message(response_text,
                             resp.channel_url)  # send the message, always add resp.channel_url as the second argument
        chatbot.stop_typing_indicator(resp.channel_url)
        chatbot.send_snoomoji('partyparrot', resp.channel_url)  # and send a snoomoji cuz why not??
        return True  # return true if you want to be done with checking the other hooks, otherwise return None or False
        # keep in mind that first added hooks get executed first


# now everytime someone says "!roll 1 100", the bot will roll a dice between 1 and 100 and send the result!


# there are also host actions availabe but ofc they require the bot account to be the host of the chatroom
@chatbot.event.on_message
def keeper_of_decency(resp):
    if resp.message == "*some very bad slur word*":
        chatbot.kick_user(channel_url=resp.channel_url, user_id=resp.user.guest_id, duration=600)  # duration is in secs
        chatbot.send_message(f'i banned {resp.user.name} for 10 mins', resp.channel_url)
        return True
    elif resp.message == "*another bad word*":
        chatbot.delete_mesg(channel_url=resp.channel_url, msg_id=resp.msg_id)
        chatbot.send_message(f"i deleted {resp.user.name}'s message", resp.channel_url)
        return True


# or you can add a basic response hook directly like so:
chatbot.set_respond_hook(input_="Hi", response="Hello {nickname}! sup?", limited_to_users=None, lower_the_input=False,
                         exclude_itself=True, must_be_equal=True,
                         limited_to_channels=["my cozy chat group"])  # you can limit by indicating chatroom's name

# you can add a welcome message for newly joined users:
chatbot.set_welcome_message("welcome to the my cozy chat group u/{nickname}!)",
                            limited_to_channels=["my cozy chat group"])

# and a farewell message too:
chatbot.set_farewell_message("Too bad u/{nickname} left us :(", limited_to_channels=["my cozy chat group"])


# there are also other types of hooks like this one for invitations
@chatbot.event.on_invitation
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
    return True


# or on ready hook
@chatbot.event.on_ready
def report_channels(_):
    channels = chatbot.get_channels()
    print("up and running in these channels!: ")
    for channel in channels:
        print(channel.name)


# wanna check invitations on start? i got you
@chatbot.event.on_ready
def check_invites(_):
    invites = chatbot.get_chat_invites()
    for invite in invites:
        chatbot.accept_chat_invite(invite.channel_url)
    return True


# and finally, run forever...
chatbot.run_4ever(auto_reconnect=True)
# set auto_reconnect to True so as to re-connect in case remote server shuts down the connection after some period of time
```


Some other fun stuff you can do with this..
-------------------------------------------------------

**Save chatroom messages to a text file (or even in an sql database or some other sht)**

```python
messages_f_handle = open('reddit-chat-msgs.txt', 'w')

@chatbot.on_message_hook
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
latest_messages = {}

@chatbot.on_message_hook
def save_msg_ids(resp):
    latest_messages.update({resp.msg_id: resp.message})

@chatbot.on_message_deleted_hook
def catch_deleted_messages(resp):
    chatbot.send_message(f"this message was deleted: {latest_messages.get(resp.msg_id)}", resp.channel_url)
```
