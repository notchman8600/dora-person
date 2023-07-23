# Standard Library
import queue
import threading

# Third Party Library
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
        pool_reset_session=True,
        block=True,
        timeout=0,
    ):
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

    def get_connection(self):
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
