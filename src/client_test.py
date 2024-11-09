from asyncio import run

from aiohttp import ClientSession
from telethon.tl.functions.messages import RequestAppWebViewRequest
from telethon.tl.types import InputBotAppShortName, InputUser

from telegram import TFAFrontendClient


async def main():
    url = "http://127.0.0.1:8000/api/client/send_pickle_request"
    async with ClientSession() as session:

        client = TFAFrontendClient(url=url, session=session)
        peer = await client.get_entity("BlumCryptoBot")
        data = await client(RequestAppWebViewRequest(
            peer=peer,
            app=InputBotAppShortName(bot_id=InputUser(peer.id, access_hash=peer.access_hash), short_name="app"),
            platform='android',
            write_allowed=True,
            start_param=None
        ))
        print(data)


if __name__ == '__main__':
    try:
        run(main())
    except SystemExit:
        pass

