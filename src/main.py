from asyncio import run

from configs import SESSIONS_PATH
from trs import TRSBackendClient, TRSManager


async def main():
    manager = TRSManager(SESSIONS_PATH)
    client = manager.get_client("test")
    async with client:
        me = await client.get_me()
        print(me)

if __name__ == '__main__':
    run(main())