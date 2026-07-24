"""A pooled MySQL connector that reconnects stale pooled connections."""

import queue
import threading

from mysql.connector.errors import InterfaceError, PoolError
from mysql.connector.pooling import MySQLConnectionPool, PooledMySQLConnection


class SafeMySQLPoolingConnector(MySQLConnectionPool):
    def __init__(
        self,
        host: str,
        user: str,
        password: str,
        db_name: str,
        port: str,
        pool_name: str,
        pool_size: int = 10,
        pool_reset_session: bool = True,
        block: bool = True,
        timeout: int = 0,
    ) -> None:
        self.host = host
        self.user = user
        self.password = password
        self.db_name = db_name
        self.port = port
        self.block = block
        self.timeout = timeout
        super().__init__(
            pool_size=pool_size,
            pool_name=pool_name,
            pool_reset_session=pool_reset_session,
            host=self.host,
            user=self.user,
            passwd=self.password,
            database=self.db_name,
            port=self.port,
        )

    def get_connection(self) -> PooledMySQLConnection:
        with threading.RLock():
            try:
                cnx = self._cnx_queue.get(block=self.block, timeout=self.timeout)
            except queue.Empty as err:
                raise PoolError("Failed getting connection; pool exhausted") from err

            if not cnx.is_connected() or self._config_version != cnx.pool_config_version:
                cnx.config(**self._cnx_config)
                try:
                    cnx.reconnect()
                except InterfaceError:
                    self._queue_connection(cnx)
                    raise
                cnx.pool_config_version = self._config_version

            return PooledMySQLConnection(self, cnx)
