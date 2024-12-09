from os import environ

from pathlib import Path

PROJECT_SOURCES_PATH = Path(__file__).parent.parent
RESOURCES_PATH = Path(PROJECT_SOURCES_PATH.parent, "resources")
SESSIONS_PATH = Path(RESOURCES_PATH, "sessions")

SERVER_PORT = 3000
try:
    SERVER_PORT = int(environ.get("SERVER_PORT"))
except Exception:
    pass

SERVER_HOST = environ.get("SERVER_HOST") or "localhost"
