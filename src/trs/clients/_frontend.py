import typing
from aiohttp import ClientSession
from pickle import dumps as pickle_dump, loads as pickle_loads

from telethon.client import AccountMethods, AuthMethods, DownloadMethods, DialogMethods, ChatMethods, UpdateMethods, \
    ButtonMethods, UploadMethods, MessageMethods, BotMethods, MessageParseMethods, UserMethods

from telethon._updates import EntityCache as MbEntityCache  # todo fix access to a protected member _updates of a module


class TRSFrontendClient(
    AccountMethods, AuthMethods, DownloadMethods, DialogMethods, ChatMethods, BotMethods,
    MessageMethods, UploadMethods, ButtonMethods, UpdateMethods, MessageParseMethods, UserMethods
):
    _proxy: typing.Optional[str]
    _session: ClientSession
    _url = str

    def __init__(self, url: str, session: ClientSession, *, proxy: typing.Union[tuple, dict] = None):
        self._session = session
        self._proxy = proxy
        self._url = url
        self._mb_entity_cache = MbEntityCache()

    async def __call__(self, request, ordered=False, flood_sleep_threshold=None):
        dump = pickle_dump(request)
        headers = {"content-type": "application/python-pickle"}
        async with self._session.post(self._url, headers=headers, data=dump) as response:
            if response.status == 200:
                data = await response.content.read()
                return pickle_loads(data)
            error = await response.json()
            raise TypeError(error.get("error"))

    async def _call(self, sender, request, ordered=False, flood_sleep_threshold=None):
        print(sender, request, ordered, flood_sleep_threshold)

    @property
    def proxy(self) -> typing.Optional[str]:
        return self._proxy
