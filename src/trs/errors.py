class TelegramRemoteSessionException(Exception):
    def __init__(self, message):
        self.message = message


class SessionNotExits(TelegramRemoteSessionException):
    pass

class TRSBackendError(TelegramRemoteSessionException):
    pass

class BackendSessionNotAuthed(TRSBackendError):
    pass