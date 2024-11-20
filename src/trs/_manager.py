import typing
from pathlib import Path

from telethon.sessions.sqlite import EXTENSION

from .sessions import TRSessionParameters
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

    def get_available_sessions_names(self) -> typing.List[str]:
        return [*self._sessions.keys()]

    def get_client(self, name: str) -> TRSBackendClient:
        if name not in self._sessions:
            raise SessionNotExits(f"Session with name '{name}' not found")
        return self._sessions[name]

    def create_client(self, name: str, session_params: TRSessionParameters) -> TRSBackendClient:
        session_path = self.sessions_path.joinpath(f"{name}{EXTENSION}")
        client = TRSBackendClient.create_from(session_path, session_params)
        self._sessions[name] = client
        return client
