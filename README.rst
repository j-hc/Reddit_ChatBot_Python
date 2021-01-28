=================
Reddit ChatRoom
=================

a fully functional (almost) bot library for reddit chatrooms!

no selenium no bullsh*t, just directly websocket

works either with reddit username & password or the api token (not a regular one you get from your registered app)

re-authentication prior to auto reconnect is only possible with PasswordAuth


Installation
============

.. code:: bash

    pip install Reddit-ChatBot-Python

required:

.. code:: bash

    python<=3.8.7

packages:

.. code:: bash

    websocket_client
    requests
    numpy
    wsaccel

wsaccel and numpy are for extra performance in websocket operations


Example
========

.. code:: python

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
    def roll(resp):  # resp is a SimpleNamespace that carries all the data of the received frame
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

    # or you can add a basic response hook directly like so:
    chatbot.set_respond_hook(input_="Hi", response="Hello {nickname}! sup?", limited_to_users=None, lower_the_input=False,
                             exclude_itself=True, must_be_equal=True, limited_to_channels=["my cozy chat group"]) # you can limit by indicating chatroom's name

    # you can add a welcome message for newly joined users:
    chatbot.set_welcome_message("welcome to the my cozy chat group u/{nickname}!)", limited_to_channels=["my cozy chat group"])

    # and a farewell message too:
    chatbot.set_farewell_message("Too bad u/{nickname} left us :()", limited_to_channels=["my cozy chat group"])


    # and finally, run forever...
    chatbot.run_4ever(auto_reconnect=True)  # set auto_reconnect so as to re-connect in case remote server shuts down the connection after some period of time



Instance of a MESG Frame (regular chat message)
================================================

.. code-block:: json

    {
      "msg_id": *msg id int*,
      "is_op_msg": false,
      "is_guest_msg": true,
      "message": "*msg*",
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
        "guest_id": "*thing id*",
        "friend_discovery_key": null,
        "role": "",
        "friend_name": null,
        "id": *user id int*,
      },
    }

You can access stuff from resp like this:

.. code:: python

    message = resp.message
    nickname = resp.user.name

Showcase of some other fun stuff you can do with this..
=======================================================

**Save chatroom messages to a text file (or even in an sql database or some other sht)**

.. code:: python

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


**Catch deleted messages**

.. code:: python

    @chatbot.after_message_hook(frame_type='DELM')
    def catch_deleted_messages(resp):
        catched_deleted_message_id = resp.msg_id


**Catch who invited who**

.. code:: python

    @chatbot.after_message_hook(frame_type='SYEV')
    def catch_invitees_and_inviters(resp):
        try:
            inviter = resp.data.inviter.nickname
            invitees = [invitee.nickname for invitee in resp.data.invitees]
        except AttributeError:
            return