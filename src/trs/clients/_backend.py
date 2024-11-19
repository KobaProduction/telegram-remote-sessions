import typing
from asyncio import AbstractEventLoop
from logging import Logger
from pathlib import Path

from telethon import TelegramClient
from telethon.network import Connection, ConnectionTcpFull

from ..sessions import TelegramRemoteSQLiteSession, TelegramRemoteSessionParameters


class TRSBackendClient(TelegramClient):
    session: TelegramRemoteSQLiteSession
    _proxy: typing.Optional[str]

    def __init__(self,
                 session: 'typing.Union[Path, TelegramRemoteSQLiteSession]', *,
                 connection: 'typing.Type[Connection]' = ConnectionTcpFull,
                 use_ipv6: bool = False,
                 proxy: typing.Union[tuple, dict] = None,
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
        if not isinstance(session, (Path, TelegramRemoteSQLiteSession)):
            raise TypeError(
                'The given session must be a Path object or a TFAClient (from TelethonFastAPI) instance.'
            )
        if isinstance(session, Path):
            session = TelegramRemoteSQLiteSession(session)
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
            proxy=proxy,
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

    @property
    def proxy(self) -> typing.Optional[str]:
        return self._proxy

    @classmethod
    def create_from(cls, session_path: Path, session_params: TelegramRemoteSessionParameters) -> 'TRSBackendClient':
        return cls(TelegramRemoteSQLiteSession(session_path, session_params))
