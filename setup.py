
from revChatGPT.ChatGPT import Chatbot

config = {
  "email": "email",
  "password": "password",
  "captcha": "api_key"
}


chatbot = Chatbot({
  "session_token": "session_token"
}, conversation_id=None, parent_id=None)



def __init__(self, config, conversation_id=None, debug=False, refresh=True):
        """
        :param config: Config dict
        :param conversation_id: Conversation ID. If None, a new conversation will be created
        :param debug: Debug mode, Default is False
        :param refresh: Refresh the session token, Default is True
        """

    
def get_chat_response(self, prompt, output="text"):
        """
        :param prompt: The message sent to the chatbot
        :param output: Output type. Can be "text" or "stream"
        :return: Response from the chatbot
        """
def rollback_conversation(self):
        """
        Rollback the conversation to the previous state
        :return: None
        """
def refresh_session(self):
        """
        Refresh the session token
        :return: None
        """
def login(self, email, password):
        """
        :param email: Email
        :param password: Password
        """
