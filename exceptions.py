class TokenNotFoundException(Exception):
    def __str__(self): return "No BOT_TOKEN found in env."

class ChatIdNotFoundException(Exception):
    def __str__(self): return "No CHAT_ID found in env."

class InvalidTokenException(Exception):
    def __str__(self): return "Invalid token."

