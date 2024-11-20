from pathlib import Path
from telethon.sessions import SQLiteSession

from ._entities import TRSessionParameters


class SQLiteTRSession(SQLiteSession):
    def __init__(self, session_path: Path, session_params: TRSessionParameters = None):
        if not isinstance(session_path, Path):
            raise TypeError('session_path argument must be only a Path object!')

        if session_path.exists() and session_params:
            raise FileExistsError(f"Session already exist, but you try create new!")

        if not session_path.exists() and not isinstance(session_params, TRSessionParameters):
            raise FileNotFoundError(
                f"Session with path does not exist and session_params is not TFASessionParameters type!"
            )

        super().__init__(str(session_path))
        self.__session_params = session_params
        self._write_session_params()

    def _write_session_params(self, ) -> None:
        keys = ("api_id", "api_hash", "device_model", "system_version", "app_version", "lang_code", "system_lang_code")
        c = self._cursor()
        c.execute("select name from sqlite_master where type='table' and name='session_parameters'")
        if c.fetchone():
            c.execute(f"select {','.join(keys)} from session_parameters")
            self.__session_params = TRSessionParameters.model_validate(dict(zip(keys, c.fetchone())))
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
            dict_session_params = self.__session_params.model_dump(by_alias=False)
            values = ",".join({key: f"'{dict_session_params[key]}'" for key in keys}.values())
            c.execute(f"insert into session_parameters values ({values})")
            c.close()
            self.save()

    @property
    def session_params(self) -> TRSessionParameters:
        return self.__session_params
