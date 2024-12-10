from asyncio import run
from os import environ

from aiohttp import ClientSession
from telethon.tl.functions.messages import RequestAppWebViewRequest
from telethon.tl.types import InputBotAppShortName, InputUser

from configs import SESSIONS_PATH, SERVER_PORT, SERVER_HOST
from trs import TRSFrontendClient, TRSManager, TRSessionParameters, TRSBackendClient
from trs.sessions import TRSessionState


async def main():
    url = f"http://{SERVER_HOST}:{SERVER_PORT}/api/v1/trs/client/send_pickle_request"
    async with ClientSession() as session:
        client = TRSFrontendClient(url=url, session=session)
        peer = await client.get_entity("BlumCryptoBot")
        data = await client(RequestAppWebViewRequest(
            peer=peer,
            app=InputBotAppShortName(bot_id=InputUser(peer.id, access_hash=peer.access_hash), short_name="app"),
            platform='android',
            write_allowed=True,
            start_param=None
        ))
        print(data)


async def create_session():

    client_name = "test"

    session_params = TRSessionParameters(
        api_id=int(environ.get("API_ID")),
        api_hash=environ.get("API_HASH"),
        app_version="0.1",
        lang_code="ru",
        system_version="Windows 11 x64",
        system_lang_code="ru",
        device_model="Motherboard model"
    )
    manager = TRSManager(sessions_path=SESSIONS_PATH)
    client: TRSBackendClient
    try:
        client = await manager.create_client(name=client_name, session_params=session_params)
    except FileExistsError:
        client = await manager.get_client(name=client_name)


    # client.set_proxy("socks5://127.0.0.1:2080")
    print(f"Client: {client_name}. Active: {client.session.active}, state: {client.session.state}, proxy: {client.session.proxy}")
    await client.connect()

    match client.session.state:
        case TRSessionState.NOT_AUTHENTICATED | TRSessionState.BROKEN:
            phone = environ.get("TEST_CLIENT_PHONE")
            send_code_status = await client.send_code_request(phone=phone)
            print(send_code_status)
            code = input("Press enter code: ")
            user = await client.sign_in(phone=phone, code=code)
            print(user)
        case TRSessionState.AUTHENTICATED:
            entity = await client.get_entity("arthur_koba")
            print(f"Entity: {entity}")
            # await client.send_message(entity=entity, message="Hello World!")
    await client.disconnect()

if __name__ == '__main__':
    try:
        run(main())
    except SystemExit:
        pass
