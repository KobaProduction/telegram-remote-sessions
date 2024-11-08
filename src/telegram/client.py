import typing
from asyncio import AbstractEventLoop
from logging import Logger
from pathlib import Path

from pydantic import BaseModel
from telethon import TelegramClient
from telethon.network import Connection, ConnectionTcpFull
from telethon.sessions import SQLiteSession


class TFASessionParameters(BaseModel):
    api_id: int
    api_hash: str
    device_model: str
    system_version: str
    app_version: str
    lang_code: str
    system_lang_code: str



class TFASession(SQLiteSession):
    def __init__(self, session_path: Path, session_params: TFASessionParameters = None):
        if not isinstance(session_path, Path):
            raise TypeError('session_path argument must be only a Path object!')

        session_path = Path(f"{session_path}.session")

        if session_path.exists() and session_params:
            raise FileExistsError(f"Session already exist, but you try create new!")

        if not session_path.exists() and not isinstance(session_params, TFASessionParameters):
            raise FileNotFoundError(
                f"Session with path does not exist and session_params is not TFASessionParameters type!"
            )

        super().__init__(str(session_path))
        self.__session_params = session_params
        self._write_session_params()

    def _write_session_params(self, ) -> None:
        c = self._cursor()
        c.execute("select name from sqlite_master where type='table' and name='session_parameters'")
        if c.fetchone():
            keys = ("api_id", "api_hash", "device_model", "system_version", "app_version", "lang_code", "system_lang_code")
            c.execute(f"select {','.join(keys)} from session_parameters")
            self.__session_params = TFASessionParameters.model_validate(dict(zip(keys, c.fetchone())))
            c.close()
            self.save()
        else:
            self._create_table(
                c,
                """session_parameters (
                    api_id integer primary key,
                    api_hash text,
                    device_model text,
                    system_version text,
                    app_version text,
                    lang_code text,
                    system_lang_code text
                )"""
            )
            values = ",".join(map(lambda x: f"'{x}'", dict(self.__session_params).values()))
            c.execute(f"insert into session_parameters values ({values})")
            c.close()
            self.save()

    @property
    def session_params(self) -> TFASessionParameters:
        return self.__session_params




class TFAClient(TelegramClient):
    def __init__(self, session: 'typing.Union[Path, TFASession]', *,
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
        if not isinstance(session, (Path, TFASession)):
            raise TypeError(
                'The given session must be a Path object or a TFAClient (from TelethonFastAPI) instance.'
            )
        if isinstance(session, Path):
            session = TFASession(session)
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
    @classmethod
    def create_from(cls, session_path: Path, session_params: TFASessionParameters) -> 'TFAClient':
        return cls(TFASession(session_path, session_params))