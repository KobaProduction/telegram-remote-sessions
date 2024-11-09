from telegram import TFAManager, TFABackendClient

from configs import SESSIONS_PATH


class Context:
    def __init__(self):
        self.session_manager = TFAManager(SESSIONS_PATH)

    def get_session_manager(self) -> TFAManager:
        return self.session_manager

    def get_client(self, session_name: str = "test") -> TFABackendClient:
        return self.session_manager.get_client(session_name)

context = Context()