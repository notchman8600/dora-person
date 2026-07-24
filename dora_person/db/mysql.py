"""Concrete :class:`DBInfraInterface` backed by mysql-connector-python."""

from typing import Any

from dora_person.config import Settings
from dora_person.db.connector import SafeMySQLPoolingConnector
from dora_person.db.interface import DBInfraInterface
from dora_person.errors import Error


class MySqlDB(DBInfraInterface):
    def __init__(self, db_conn: SafeMySQLPoolingConnector) -> None:
        self.__db_conn = db_conn

    def query(self, statement: str, *args: Any) -> tuple[list, Error | None]:
        connection = self.__db_conn.get_connection()
        try:
            cursor = connection.cursor(prepared=True)
            cursor.execute(statement, args)
            result = cursor.fetchall()
            if result is None:
                return [], Error(code=500, message="failed to query")
        except Exception as e:
            cursor.close()
            connection.close()
            return [], Error(code=500, message=f"failed to query: {e}")
        finally:
            cursor.close()
            connection.close()
        return result, None

    def execute(self, statement: str, *args: Any) -> tuple[Any, Error | None]:
        connection = self.__db_conn.get_connection()
        try:
            cursor = connection.cursor(prepared=True)
            cursor.execute(statement, args)
            connection.commit()
        except Exception as e:
            cursor.close()
            connection.close()
            return [], Error(code=500, message=f"failed to query: {e}")
        finally:
            cursor.close()
            connection.close()
        return cursor.rowcount, None


def create_mysql_db(settings: Settings) -> MySqlDB:
    """Build a :class:`MySqlDB` from settings.

    Connection details are read lazily here (rather than at import time) so the
    application and its tests can be imported without a live database.
    """

    return MySqlDB(
        SafeMySQLPoolingConnector(
            host=settings.mysql_db_host,
            user=settings.mysql_db_user,
            password=settings.mysql_db_pass,
            db_name=settings.mysql_db_name,
            port=settings.mysql_db_port,
            pool_size=settings.mysql_pool_size,
            pool_name=settings.mysql_pool_name,
            block=True,
        )
    )
