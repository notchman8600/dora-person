# Standard Library
import os
from typing import Any

# First Party Library
from dora_person.db_interface import DBInfraInterface
from dora_person.error import Error
from dora_person.mysql.db_connetor import SafeMySQLPoolingConnector


class MySqlDB(DBInfraInterface):
    __db_conn: SafeMySQLPoolingConnector

    def __init__(
        self,
        db_conn: SafeMySQLPoolingConnector,
    ) -> None:
        # インスタンスを注入
        self.__db_conn = db_conn

    def query(self, statement: str, *args) -> tuple[list, Error | None]:
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
            return [], Error(code=500, message="failed to query: {}".format(e))
        finally:
            cursor.close()
            connection.close()
        return result, None

    def execute(self, statement: str, *args) -> tuple[Any, Error | None]:
        connection = self.__db_conn.get_connection()
        try:
            cursor = connection.cursor(prepared=True)
            cursor.execute(statement, args)
            connection.commit()
        except Exception as e:
            cursor.close()
            connection.close()
            return [], Error(code=500, message="failed to query: {}".format(e))

        finally:
            cursor.close()
            connection.close()
        return cursor.rowcount, None


mysql_instance = MySqlDB(
    SafeMySQLPoolingConnector(
        host=os.environ["MYSQL_DB_HOST"],
        user=os.environ["MYSQL_DB_USER"],
        password=os.environ["MYSQL_DB_PASS"],
        db_name=os.environ["MYSQL_DB_NAME"],
        port=os.environ["MYSQL_DB_PORT"],
        pool_size=30,
        pool_name="n4u-mysql",
        block=True,
    )
)
