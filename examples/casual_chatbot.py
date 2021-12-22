from Reddit_ChatBot_Python import ChatBot, RedditAuthentication, CustomType
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
    if resp.channel_type == CustomType.group:
        invit_type = "group chat"
    elif resp.channel_type == CustomType.direct:
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


# reading last 50 messages from a channel
@chatbot.event.on_ready
def report_channels(_):
    channels = chatbot.get_channels()
    for channel in channels:
        if channel.name == "My Channel":
            last_fifty_message = chatbot.get_older_messages(channel_url=channel.channel_url, prev_limit=50)


# starting a direct chat
@chatbot.event.on_ready
def dm(_):
    dm_channel = chatbot.create_direct_channel("someuseridk")
    chatbot.send_message("Hey what's up?", dm_channel.channel_url)


# starting a group chat
@chatbot.event.on_ready
def dm(_):
    dm_channel = chatbot.create_channel(nicknames=["user1", "user2"], group_name="my group")
    chatbot.send_message("Hey guys what's up?", dm_channel.channel_url)


# wanna check invitations on start? i got you
@chatbot.event.on_ready
def check_invites(_):
    invites = chatbot.get_chat_invites()
    for invite in invites:
        print(f"invited to chat by {invite.inviter} with the message {invite.last_message.message}")
        chatbot.accept_chat_invite(invite.channel_url)
    return True


# and finally, run forever...
chatbot.run_4ever(auto_reconnect=True)
# set auto_reconnect to True so as to re-connect in case remote server shuts down the connection after some period of time