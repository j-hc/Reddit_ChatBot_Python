=================
Reddit ChatRoom
=================

a pretty basic websocket wrapper for reddit chatrooms by `u/peroksizom <http://reddit.com/user/peroksizom>`_


Installation
============

add it as a submodule to your project like so

.. code:: bash

  git submodule add https://github.com/scrubjay55/Reddit_ChatBot_Python

or you can just git clone it


required packages:

.. code:: bash

  websocket_client>=0.57.0
  requests>=2.24.0


Usage
========

.. code:: python

  from Reddit_ChatBot_Python.ChatBot import ChatBot

  # get channels' sendbird channel urls
  # this is not mandatory at all but useful for seeing which sub the message came from, else u will just see @None in front of names
  sub_channels = ["Turkey", "AskReddit"]
  
  # instantiate a chatbot and pass in the sub_channels if you want
  chatbot = ChatBot(reddit_api_token="**YOUR API TOKEN**", sub_channels=sub_channels, print_chat=True, enable_trace=False)
  # reddit_api_token is the classic Bearer token for reddit api operations
  # keep in mind that atm the bot only fetches a 7-day-limited sendbird key and bearer tokens only last one hour
  # which mean bot will needed to be restarted every 7 day

  # grab the websocket
  websock = chatbot.WebSocketClient
  # now you can add hooks to the websock object in order for them to be executed when a message is received like so:
  
  # create a function to hook
  def roll(resp):  #  resp is a FrameModel object that carries all the data of the received, you can see other FrameModel props as well
      if resp.type_f == "MESG": #  MESG is the type of the ordinary chat messages 
          messg_s = resp.message.split()
          if messg_s[0] == "!roll" and len(messg_s) == 3:  # if received message says !roll
              limit_bottom = messg_s[1]
              limit_top = messg_s[2]

              rolled_number = random.randint(int(limit_f), int(limit_u))
              response_text = f"@{resp.user_name} {rolled_number}. Better luck next time!"
              # a basic roll game

              websock.send_message(response_text, resp.channel_url) # and send the message finally, always add resp.channel_url as the second argument
              websock.send_snoomoji('partyparrot', resp.channel_url)  # and send a snoomoji cuz why not
              return True  # return true if you want to be done with checking the other hooks, otherwise return None
                           # keep in mind that first added hooks gets executed first

  websock.add_after_message_hook(roll)  # add the hook
  # now everytime someone says "!roll 1 100", the bot will roll and send the result!

  # or you can add a basic response hook directly like so:
  websock.set_respond_hook(input_="Hi", response="Hello and welcome!", limited_to_users=None, lower_the_input=False,
                                                                      exclude_itself=True, must_be_equal=True, quote_parent=False)

  # and finally, run forever...
  websock.run_4ever()
