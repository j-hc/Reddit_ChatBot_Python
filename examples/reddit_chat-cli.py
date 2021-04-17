from Reddit_ChatBot_Python import ChatBot, RedditAuthentication
from threading import Thread
from time import sleep

reddit_authentication = RedditAuthentication.PasswordAuth(reddit_username="", reddit_password="")

chatbot = ChatBot(print_chat=True, store_session=True, log_websocket_frames=False, authentication=reddit_authentication)

global TARGET_CHANNEL_URL


@chatbot.event.on_ready
def get_target_channel_url(_):
    global TARGET_CHANNEL_URL
    TARGET_CHANNEL_URL = chatbot.get_channels()[0].channel_url


Thread(target=chatbot.run_4ever, daemon=True).start()

sleep(3)
while True:
    chatbot.send_message(input(), TARGET_CHANNEL_URL)
