from abc import *
from typing import Any, Dict

import pymysql
from impala.dbapi import connect


class BaseConnectorMeta(metaclass=ABCMeta):

    @abstractmethod
    def connect(self) -> Any:
        """
        connection을 반환
        """
        pass


class HiveConnector(BaseConnectorMeta):
    def __init__(self, host, port, user, password, database, **kwargs) -> None:
        self._host = host
        self._port = port
        self._user = user
        self._password = password
        self._database = database
        self._kwargs = kwargs            # 명시된 필수 컬럼외에 추가하고 싶은 옵션

    def connect(self, **kwargs) -> Any:
        return connect(
            host=self._host,
            port=self._port,
            user=self._user,
            password=self._password,
            database=self._database,
            **self._kwargs
        )


class MariadbConnector(BaseConnectorMeta):
    def __init__(
            self,
            host: str,
            port: int,
            user: str,
            password: str,
            database: str,
            **kwargs: Dict[str, Any]
    ) -> None:
        self._host = host
        self._port = port
        self._user = user
        self._password = password
        self._database = database
        self._kwargs = kwargs               # 명시된 필수 컬럼외에 추가하고 싶은 옵션

    def connect(self) -> Any:
        return pymysql.connect(
            host=self._host,
            port=self._port,
            user=self._user,
            password=self._password,
            db=self._database,
            **self._kwargs
        )
