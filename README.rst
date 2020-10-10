=================
Reddit ChatRoom
=================

a pretty basic websocket wrapper for reddit chatrooms by `u/peroksizom <http://reddit.com/user/peroksizom>`_

no selenium no bullsh*t, just directly websocket

works with the api token (not a regular one you get from your registered app), so you wont have to expose your pass

there is a script to dump sendbird access scoped token available `here <https://github.com/scrubjay55/Reddit_ChatBot_Python/blob/master/dump_access_token/dump_access_token.py>`_


Installation
============

.. code:: bash

    pip install Reddit-ChatBot-Python

required packages:

.. code:: bash

    websocket_client>=0.57.0
    requests>=2.24.0


Usage
========

.. code:: python

  from Reddit_ChatBot_Python.ChatBot import ChatBot
  
  # instantiate a chatbot and pass in the sub_channels if you want
  chatbot = ChatBot(global_blacklist_words={'a', 'b'},  # you can define words that shouldnt be sent (this migth be handy for slurs)
                    global_blacklist_users={'a', 'b'},  # hooks never get executed for users in this list
                    print_chat=True, store_session=True, dont_answer_blocked=True,  # some parameters u might wanna know
                    reddit_api_token="**YOUR API TOKEN**")
  # reddit_api_token is a sendbird access scoped token. there is a dump script available.
  # keep in mind that atm the bot only fetches a 7-days-limited sendbird access key and api tokens only last one hour
  # which means the bot will needed to be restarted every 7 days with a new api key

  # grab the websocket
  websock = chatbot.WebSocketClient

  # you can add a rate limit like so:
  websock.RateLimiter.is_enabled = True
  websock.RateLimiter.max_calls = 23  # how many messages will be sent by the bot
  websock.RateLimiter.period = 1.5  # in what period(in minutes)

  # now you can add hooks to the websock object in order for them to be executed when a message is received like so:
  
  # create a function and hook

  @websock.after_message_hook
  def roll(resp):  #  resp is a namedtuple that carries all the data of the received frame
      if resp.type_f == "MESG": #  MESG is the type of the ordinary chat messages. you can see others here: https://github.com/scrubjay55/Reddit_ChatBot_Python/blob/master/Utils/FrameModel/FrameModel.py
                                #  Dont forget to perform this check if you are just gonna do stuff with regular chat messages
          messg_s = resp.message.split()
          if messg_s[0] == "!roll" and len(messg_s) == 3:  # if received message says !roll
              limit_bottom = messg_s[1]
              limit_top = messg_s[2]

              rolled_number = random.randint(int(limit_f), int(limit_u))
              response_text = f"@{resp.user.name} {rolled_number}. Better luck next time!"
              # a basic roll game

              websock.send_message(response_text, resp.channel_url) # and send the message, always add resp.channel_url as the second argument
              websock.send_snoomoji('partyparrot', resp.channel_url)  # and send a snoomoji cuz why not
              return True  # return true if you want to be done with checking the other hooks, otherwise return None
                           # keep in mind that first added hooks gets executed first

  # now everytime someone says "!roll 1 100", the bot will roll and send the result!

  # or you can add a basic response hook directly like so:
  websock.set_respond_hook(input_="Hi", response="Hello {nickname}! enjoy your time in r/askreddit chatroom", limited_to_users=None, lower_the_input=False,
                                                                      exclude_itself=True, must_be_equal=True, limited_to_channels=["AskReddit"])
  # you can add a welcome message for newly joined users too:
  websock.set_welcome_message("welcome to the r/askreddit chatroom u/{nickname}!", limited_to_channels=["AskReddit"])  # you can limit by indicating chatroom's name

  # and finally, run forever...
  websock.run_4ever(auto_reconnect=True)  # set auto_reconnect so as to re-connect in case remote server shuts down the connection after some period of time
