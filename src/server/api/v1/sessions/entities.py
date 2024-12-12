import typing

from better_proxy import Proxy
from pydantic import BaseModel

from trs import TRSessionParameters


class FullSessionInfo(BaseModel):
    is_active: bool
    is_authenticated: bool
    is_broken: bool
    proxy: str | None
    session_parameters: TRSessionParameters


class SessionList(BaseModel):
    sessions: typing.List[str]


class SessionResponseStatus(BaseModel):
    status: bool
    message: str


class SessionAuthCodeHash(BaseModel):
    phone: str
    hash: str


class SessionAuthUser(BaseModel):
    id: int
    username: str
    first_name: str
    last_name: str
