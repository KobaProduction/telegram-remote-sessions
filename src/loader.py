from telegram import TFAManager

from configs import SESSIONS_PATH

session_manager = TFAManager(SESSIONS_PATH)

def get_session_manager() -> TFAManager:
    return session_manager