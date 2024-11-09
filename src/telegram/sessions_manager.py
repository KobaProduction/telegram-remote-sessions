import typing
from pathlib import Path

from . import TFABackendClient, TFASessionParameters
from .errors import SessionNotExits

class TFAManager:
    _sessions: dict[str, TFABackendClient] = {}

    def __init__(self, sessions_path: Path):
        self.sessions_path = sessions_path
        self._load_sessions()

    def _load_sessions(self):
        for file in self.sessions_path.glob("*.session"):
            name = ".".join(file.name.split(".")[:-1])
            self._sessions.update({name: TFABackendClient(file)})

    def get_available_sessions_names(self) -> typing.List[str]:
        return [*self._sessions.keys()]

    def get_client(self, name: str) -> TFABackendClient:
        if name not in self._sessions:
            raise SessionNotExits(f"Session with name '{name}' not found")
        return self._sessions[name]

    def create_client(self, name: str, session_params: TFASessionParameters) -> TFABackendClient:
        session_path = self.sessions_path.joinpath(f"{name}.session")
        client = TFABackendClient.create_from(session_path, session_params)
        self._sessions[name] = client
        return client