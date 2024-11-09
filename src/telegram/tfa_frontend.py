import typing
from aiohttp import ClientSession

from telethon.client import AccountMethods, AuthMethods, DownloadMethods, DialogMethods, ChatMethods, UpdateMethods, \
    ButtonMethods, UploadMethods, MessageMethods, BotMethods, MessageParseMethods, UserMethods
from telethon._updates import EntityCache as MbEntityCache

from .utils import convert_from_pre_json, convert_objects_from_dict, convert_to_pre_json


class TFAFrontendClient(AccountMethods, AuthMethods, DownloadMethods, DialogMethods, ChatMethods,
    BotMethods, MessageMethods, UploadMethods, ButtonMethods, UpdateMethods, MessageParseMethods, UserMethods):

    _proxy: typing.Optional[str]
    _session: ClientSession
    _url = str

    def __init__(self, url: str, session: ClientSession, *, proxy: typing.Union[tuple, dict] = None):
        self._session = session
        self._proxy = proxy
        self._url = url
        self._mb_entity_cache = MbEntityCache()

    async def __call__(self, request, ordered = False, flood_sleep_threshold = None):
        data = request.to_dict()
        cleaned = convert_to_pre_json(data)
        async with self._session.post(self._url, params={"ordered": str(ordered)}, json=cleaned) as response:
            result = await response.json()
            if response.status == 200:
                data = convert_from_pre_json(result.get("raw", None))
                return convert_objects_from_dict(data)
            raise Exception(result)

    async def _call(self, sender, request, ordered=False, flood_sleep_threshold=None):
        print(sender, request, ordered, flood_sleep_threshold)

    @property
    def proxy(self) -> typing.Optional[str]:
        return self._proxy