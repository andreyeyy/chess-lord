class TokenNotFoundException(Exception):
    def __str__(): return "No BOT_TOKEN found in env."

class ChatIdNotFoundException(Exception):
    def __str__(): return "No CHAT_ID found in env."

class InvalidTokenException(Exception):
    def __str__(): return "Invalid token."

