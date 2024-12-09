import typing

from pydantic import BaseModel

from trs import TRSessionParameters


class SessionName(BaseModel):
    name: str

class FullSessionInfo(SessionName):
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