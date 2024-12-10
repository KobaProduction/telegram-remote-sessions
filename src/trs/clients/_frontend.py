from aiohttp import ClientSession
from pickle import dumps as pickle_dump, loads as pickle_loads

from fastapi import status
from telethon.client import AccountMethods, AuthMethods, DownloadMethods, DialogMethods, ChatMethods, UpdateMethods, \
    ButtonMethods, UploadMethods, MessageMethods, BotMethods, MessageParseMethods, UserMethods

from telethon._updates import EntityCache as MbEntityCache  # todo fix access to a protected member _updates of a module

from trs.errors import BackendSessionNotAuthed, TRSBackendError


class TRSFrontendClient(
    AccountMethods, AuthMethods, DownloadMethods, DialogMethods, ChatMethods, BotMethods,
    MessageMethods, UploadMethods, ButtonMethods, UpdateMethods, MessageParseMethods, UserMethods
):
    def __init__(self, name: str, url: str, session: ClientSession):
        self._name = name
        self._session = session
        self._url = url
        self._mb_entity_cache = MbEntityCache()

    async def __call__(self, request, ordered=False, flood_sleep_threshold=None):
        dump = pickle_dump(request)
        params = {"session_name": self._name}
        headers = {"content-type": "application/python-pickle"}
        response = await self._session.post(self._url, params=params, headers=headers, data=dump)
        match response.status:
            case status.HTTP_200_OK:
                data = await response.content.read()
                result = pickle_loads(data)
                if isinstance(result, Exception):
                    raise result
                return result
            case status.HTTP_422_UNPROCESSABLE_ENTITY:
                error = await response.json()
                errors = ", ".join(map(lambda x: "{type} - {loc} - {msg} ({input})".format(**x), error.get("detail")))
                raise TypeError(errors)
            case status.HTTP_401_UNAUTHORIZED:
                raise BackendSessionNotAuthed("Session was not authenticated")
            case status.HTTP_400_BAD_REQUEST:
                error = await response.json()
                raise TRSBackendError(error.get("error"))
            case status.HTTP_500_INTERNAL_SERVER_ERROR:
                raise TRSBackendError(await response.text())
            case _:
                raise Exception("Unknown status code: {}".format(response.status))
