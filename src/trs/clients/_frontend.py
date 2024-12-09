from aiohttp import ClientSession
from pickle import dumps as pickle_dump, loads as pickle_loads

from telethon.client import AccountMethods, AuthMethods, DownloadMethods, DialogMethods, ChatMethods, UpdateMethods, \
    ButtonMethods, UploadMethods, MessageMethods, BotMethods, MessageParseMethods, UserMethods

from telethon._updates import EntityCache as MbEntityCache  # todo fix access to a protected member _updates of a module


class TRSFrontendClient(
    AccountMethods, AuthMethods, DownloadMethods, DialogMethods, ChatMethods, BotMethods,
    MessageMethods, UploadMethods, ButtonMethods, UpdateMethods, MessageParseMethods, UserMethods
):
    def __init__(self, url: str, session: ClientSession):
        self._session = session
        self._url = url
        self._mb_entity_cache = MbEntityCache()

    async def __call__(self, request, ordered=False, flood_sleep_threshold=None):
        dump = pickle_dump(request)
        headers = {"content-type": "application/python-pickle"}
        async with self._session.post(self._url, headers=headers, data=dump) as response:
            if response.status == 200:
                data = await response.content.read()
                result = pickle_loads(data)
                if isinstance(result, Exception):
                    raise result
                return result
            error = await response.json()
            raise TypeError(error.get("error"))
