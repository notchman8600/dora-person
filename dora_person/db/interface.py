"""Abstract database boundary used by the repository layer."""

from abc import ABCMeta, abstractmethod
from typing import Any

from dora_person.errors import Error


class DBInfraInterface(metaclass=ABCMeta):
    """A minimal SQL execution surface that repositories depend on.

    Keeping the concrete driver behind this interface lets the service and
    repository layers be unit tested with an in-memory fake.
    """

    @abstractmethod
    def query(self, statement: str, *args: Any) -> tuple[list, Error | None]:
        """Run a read statement, returning ``(rows, error)``.

        On success ``error`` is ``None``; on failure ``rows`` is empty and
        ``error`` describes the problem.
        """

        raise NotImplementedError

    @abstractmethod
    def execute(self, statement: str, *args: Any) -> tuple[Any, Error | None]:
        """Run a write statement, returning ``(affected_rows, error)``.

        On success ``error`` is ``None``; on failure the first element is an
        empty list and ``error`` describes the problem.
        """

        raise NotImplementedError
