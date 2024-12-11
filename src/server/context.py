from trs import TRSManager, TRSBackendClient

from configs import SESSIONS_PATH
from trs.errors import BackendSessionNotAuthed


class Context:
    def __init__(self):
        self.session_manager = TRSManager(SESSIONS_PATH)

    def get_session_manager(self) -> TRSManager:
        return self.session_manager

    async def get_client(self, session_name: str) -> TRSBackendClient:
        client = await self.session_manager.get_client(session_name)
        if not client.is_connected():
            await client.connect()
            me = await client.get_me()
            if not me:
                client.disconnect()
                raise BackendSessionNotAuthed(f"Session {session_name} Not Authed")
        return client


context = Context()
