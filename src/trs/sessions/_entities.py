from enum import IntEnum
from pydantic import BaseModel


class TRSessionState(IntEnum):
    NOT_AUTHENTICATED = 0
    AUTHENTICATED = 1
    BROKEN = 2


class TRSDeviceParameters(BaseModel):
    device_model: str
    system_version: str
    system_lang_code: str


class TRSApplicationParameters(BaseModel):
    app_version: str
    lang_code: str


class TRSessionParameters(TRSDeviceParameters, TRSApplicationParameters):
    api_id: int
    api_hash: str
