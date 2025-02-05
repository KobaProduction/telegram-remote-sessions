import typing
from asyncio import AbstractEventLoop
from logging import Logger
from pathlib import Path

from better_proxy import Proxy
from telethon import TelegramClient, types
from telethon.network import Connection, ConnectionTcpFull

from ..sessions import SQLiteTRSession, TRSessionParameters, TRSessionState


class TRSBackendClient(TelegramClient):
    session: SQLiteTRSession

    def __init__(self,
                 session: 'typing.Union[Path, SQLiteTRSession]', *,
                 connection: 'typing.Type[Connection]' = ConnectionTcpFull,
                 use_ipv6: bool = False,
                 proxy: typing.Union[None, str, Proxy] = None,
                 local_addr: typing.Union[str, tuple] = None,
                 timeout: int = 10,
                 request_retries: int = 5,
                 connection_retries: int = 5,
                 retry_delay: int = 1,
                 auto_reconnect: bool = True,
                 sequential_updates: bool = False,
                 flood_sleep_threshold: int = 60,
                 raise_last_call_error: bool = False,
                 loop: AbstractEventLoop = None,
                 base_logger: typing.Union[str, Logger] = None,
                 receive_updates: bool = True,
                 catch_up: bool = False,
                 entity_cache_limit: int = 5000
                 ):
        if not isinstance(session, (Path, SQLiteTRSession)):
            raise TypeError(
                'The given session must be a Path object or a TFAClient (from TelethonFastAPI) instance.'
            )
        if isinstance(session, Path):
            session = SQLiteTRSession(session)
        super().__init__(
            session,
            api_id=session.session_params.api_id,
            api_hash=session.session_params.api_hash,
            device_model=session.session_params.device_model,
            system_version=session.session_params.system_version,
            app_version=session.session_params.app_version,
            lang_code=session.session_params.lang_code,
            system_lang_code=session.session_params.system_lang_code,
            connection=connection,
            use_ipv6=use_ipv6,
            proxy=None,
            local_addr=local_addr,
            timeout=timeout,
            request_retries=request_retries,
            connection_retries=connection_retries,
            retry_delay=retry_delay,
            auto_reconnect=auto_reconnect,
            sequential_updates=sequential_updates,
            flood_sleep_threshold=flood_sleep_threshold,
            raise_last_call_error=raise_last_call_error,
            loop=loop,
            base_logger=base_logger,
            receive_updates=receive_updates,
            catch_up=catch_up,
            entity_cache_limit=entity_cache_limit
        )
        if proxy:
            self.set_proxy(proxy)
        elif session.proxy:
            self.set_proxy(session.proxy)

    def set_proxy(self, proxy: typing.Union[str, Proxy]) -> None:
        if isinstance(proxy, str):
            proxy = Proxy.from_str(proxy)
        if not isinstance(proxy, Proxy):
            raise TypeError("Proxy must be of type 'str' or 'Proxy'")
        proxy_dict = dict(
            proxy_type=proxy.protocol,
            addr=proxy.host,
            port=proxy.port,
            username=proxy.login,
            password=proxy.password
        )
        super().set_proxy(proxy_dict)

    async def get_me(self: 'TelegramClient', input_peer: bool = False) \
            -> 'typing.Union[types.User, types.InputPeerUser]':
        me = await super().get_me(input_peer=input_peer)
        if me is not None:
            self.session.set_state(TRSessionState.AUTHENTICATED)
        elif self.session.state == TRSessionState.AUTHENTICATED:
            self.session.set_state(TRSessionState.BROKEN)
        elif self.session.state != TRSessionState.BROKEN:
            self.session.set_state(TRSessionState.NOT_AUTHENTICATED)
        return me

    async def _on_login(self, user):
        self.session.set_state(TRSessionState.AUTHENTICATED)
        return await super()._on_login(user)

    @classmethod
    def create_from(cls, session_path: Path, session_params: TRSessionParameters) -> 'TRSBackendClient':
        return cls(SQLiteTRSession(session_path, session_params))
