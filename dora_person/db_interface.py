# Standard Library
from abc import ABCMeta, abstractmethod
from typing import Any

# First Party Library
from dora_person.error import Error


class DBInfraInterface(metaclass=ABCMeta):
    @abstractmethod
    def query(self, statement: str, **kwargs) -> tuple[list, Error | None]:
        """Throw query for db to get data.

        Parameters
        ------
        target : str
            The name of table.

        **kwargs : Dict
            The conditions of query.
            The keys of dict should refer the name of columns in the table.

        Returns
        ------
        result : List
            The result of query.
            When failed, return empty list.
        error : GetMsgObj
            When success, return `GetSuccess` object.
            When failure, return `GetFailure` object.
        """
        raise NotImplementedError

    @abstractmethod
    def execute(self, statement: str, **kwargs) -> tuple[Any, Error | None]:
        """insert/update/delete for db

        Parameters
        ------
        target : str
            name of table

        method : str
            "insert" or "update" or "delete"

        **kwargs : Dict
            parameters of data

        Returns
        ------
        target_id : Any
            the id of inserted record.
            when failure or not insert method, return `0`.

        error : ExecMsg
            When success, return `ExecSuccess` object.
            When failure, return `ExecFailure` object.
        """
        raise NotImplementedError
