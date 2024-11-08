class TFAException(Exception):
    def __init__(self, message):
        self.message = message

class SessionNotExits(TFAException):
    pass