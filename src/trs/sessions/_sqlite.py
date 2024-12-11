import typing
from pathlib import Path

from better_proxy import Proxy
from telethon.sessions import SQLiteSession

from ._entities import TRSessionParameters, TRSessionState


class SQLiteTRSession(SQLiteSession):
    def __init__(self, session_path: Path, session_params: TRSessionParameters = None):
        if not isinstance(session_path, Path):
            raise TypeError("session_path argument must be only a 'Path' object!")

        if session_path.exists() and session_params:
            raise FileExistsError(f"Session already exist, but you try create new!")

        if not session_path.exists() and not isinstance(session_params, TRSessionParameters):
            raise FileNotFoundError(
                f"Session with path does not exist and session_params is not 'TFASessionParameters' type!"
            )

        super().__init__(str(session_path))
        self.__session_params = session_params
        self._is_active = True
        self._proxy = None
        self._state: TRSessionState = TRSessionState.NOT_AUTHENTICATED
        self._write_session_params()

    def _write_session_params(self) -> None:
        keys = ("api_id", "api_hash", "device_model", "system_version", "app_version", "lang_code", "system_lang_code")
        c = self._cursor()
        c.execute("select name from sqlite_master where type='table' and name='session_parameters'")
        if c.fetchone():
            c.execute(f"select {','.join(keys)} from session_parameters")
            self.__session_params = TRSessionParameters.model_validate(dict(zip(keys, c.fetchone())))
            c.execute(f"select state, is_active, proxy from session_parameters")
            state, is_active, proxy = c.fetchone()
            self._is_active = bool(is_active)
            self._state = TRSessionState(state)
            self._proxy = None if not proxy else proxy
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
                    system_lang_code text,
                    state integer,
                    is_active boolean,
                    proxy text default ""
                )"""
            )
            dict_session_params = self.__session_params.model_dump(by_alias=False)
            values = ",".join({key: f"'{dict_session_params[key]}'" for key in keys}.values())
            c.execute(f"insert into session_parameters values ({values}, '0', '1', '')")
            c.close()
            self.save()

    def _set_session_parameter(self, parameter: str, value: str):
        c = self._cursor()
        c.execute(f"update session_parameters set {parameter}={value};")
        c.close()
        self.save()

    @property
    def proxy(self) -> typing.Optional[str]:
        return self._proxy

    def set_proxy(self, proxy: typing.Union[None, str, Proxy] = None):
        if not (proxy is None or isinstance(proxy, str) or isinstance(proxy, Proxy)):
            raise ValueError("proxy must be a 'None', 'str' or a 'Proxy' types")
        if isinstance(proxy, str):
            proxy = Proxy.from_str(proxy)
        if isinstance(proxy, Proxy):
            proxy = proxy.as_url
        self._proxy = proxy
        if proxy is None:
            proxy = ""
        self._set_session_parameter(parameter="proxy", value=f"'{proxy}'")

    @property
    def state(self) -> TRSessionState:
        return self._state

    def set_state(self, state: TRSessionState):
        if not isinstance(state, TRSessionState):
            raise TypeError("state argument must be only a 'SessionState' object!")
        self._set_session_parameter(parameter="state", value=str(state.value))
        self._state = state

    @property
    def active(self) -> bool:
        return self._is_active

    def activate(self):
        if self._is_active:
            return
        self._set_session_parameter(parameter="is_active", value="1")
        self._is_active = True

    def deactivate(self):
        if not self._is_active:
            return
        self._set_session_parameter(parameter="is_active", value="0")
        self._is_active = False

    @property
    def session_params(self) -> TRSessionParameters:
        return self.__session_params
