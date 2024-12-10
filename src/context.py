from trs import TRSManager, TRSBackendClient

from configs import SESSIONS_PATH


class Context:
    def __init__(self):
        self.session_manager = TRSManager(SESSIONS_PATH)

    def get_session_manager(self) -> TRSManager:
        return self.session_manager

    async def get_client(self, session_name: str) -> TRSBackendClient:
        return await self.session_manager.get_client(session_name)


context = Context()
