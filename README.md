Reddit ChatRoom
==============

a pretty basic websocket wrapper for reddit chatrooms

Installation
------------
add it as a submodule to your project like so

    git submodule add https://github.com/scrubjay55/Reddit_ChatBot_Python

Usage
-----


    from Reddit_ChatBot_Python.ChatBot import ChatBot

    # set channel id and subreddit pairs for future use
    channelid_sub_pairs = {"sendbird_group_channel_1560782_a6a04cb8bf4d2044c4344ef2a98d6b03310c6c99": "Turkey"}
	
	# create chatbot instance
    chatbot = ChatBot(key="*SESSION_KEY*", ai="*AI*", channelid_sub_pairs=channelid_sub_pairs)

    websock = chatbot.WebSocketClient
    # now you can add hooks to the websock object in order for them to be executed when a message is received like so:
	
	# create function to hook
	def roll(resp):  #  resp is a FrameModel object that carries all the data of the received
	    if resp.type_f == "MESG": #  MESG is the type of the ordinary chat messages 
	        messg_s = resp.message.split()
	        if messg_s[0] == "!roll" and len(messg_s) == 3:  # if received message says !roll
	            limit_bottom = messg_s[1]
	            limit_top = messg_s[2]

	            rolled_number = random.randint(int(limit_f), int(limit_u))
	            response_text = f"@{resp.user_name} {rolled_number}. Better luck next time!"
	            # a basic roll game

	            websock.send_message(response_text, resp.channel_url) # and send the message finally

    websock.add_after_message_hook(roll)  # add the hook
    # now everytime someone says "!roll 1 100", the bot will roll and send the result!

    # or you can add a basic response hook directly like so:
    websock.set_respond_hook(input_="Hi", response="Hello and welcome!", lower_the_input=True)

    # and finally, run forever...
    websock.run_4ever()
