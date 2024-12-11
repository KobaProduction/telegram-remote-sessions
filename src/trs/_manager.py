import typing
from pathlib import Path

from telethon.sessions.sqlite import EXTENSION

from .sessions import TRSessionParameters, TRSessionState
from .clients import TRSBackendClient
from .errors import SessionNotExits


class TRSManager:
    _sessions: dict[str, TRSBackendClient] = {}

    def __init__(self, sessions_path: Path):
        self.sessions_path = sessions_path
        self._load_sessions()

    def _load_sessions(self):
        for file in self.sessions_path.glob(f"*{EXTENSION}"):
            name = ".".join(file.name.split(".")[:-1])
            self._sessions.update({name: TRSBackendClient(file)})

    async def get_clients(self,
                          active: bool | None = None,
                          state: TRSessionState | None = None,
                          ) -> typing.List[str] | typing.List[str]:
        sessions_names = []
        for session_name, client in self._sessions.items():
            if active is not None and client.session.active != active:
                continue
            if state is not None and client.session.state != state:
                continue
            sessions_names.append(session_name)
        return sessions_names

    async def get_client(self, name: str) -> TRSBackendClient:
        if name not in self._sessions:
            raise SessionNotExits(f"Session with name '{name}' not found")
        return self._sessions[name]

    async def create_client(self, name: str, session_params: TRSessionParameters) -> TRSBackendClient:
        session_path = self.sessions_path.joinpath(f"{name}{EXTENSION}")
        client = TRSBackendClient.create_from(session_path, session_params)
        self._sessions[name] = client
        return client

    async def delete_client(self, name: str):
        client = await self.get_client(name)
        if not client.is_connected():
            await client.connect()
        if client.get_me() and await client.log_out():
            return self._sessions.pop(name)
        await client.disconnect()
        self._sessions.pop(name)
        client.session.delete()
