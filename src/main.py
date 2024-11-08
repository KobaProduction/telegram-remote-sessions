from asyncio import run

from configs import SESSIONS_PATH
from telegram import TFAClient, TFASessionParameters


async def main():
    session_name = "test"

    session_path = SESSIONS_PATH.joinpath(f"{session_name}.session")

    if not session_path.exists():

        session_params = TFASessionParameters(
            api_id=1,
            api_hash="",
            device_model="Windows Laptop",
            system_version="Windows 10",
            app_version="1.0",
            lang_code="ru",
            system_lang_code="ru"
        )
        client = TFAClient.create_from(
            session_path=session_path,
            session_params=session_params
        )
    else:
        client = TFAClient(session=session_path)
    async with client:
        me = await client.get_me()
        print(me)


if __name__ == '__main__':
    run(main())