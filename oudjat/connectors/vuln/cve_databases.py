"""A module that provides an easy CVE connectors hub."""

from enum import Enum
from typing import TYPE_CHECKING, NamedTuple

from .circl import CirclConnector
from .cveorg import CVEorgConnector
from .nist import NistConnector

if TYPE_CHECKING:
    from .cve_connector import CVEConnector


class CVEDatabaseProps(NamedTuple):
    """
    A helper clas to properly handle CVEDatabase property types.

    Attributes:
        db_name         : The name of the database
        connector       : The connector associated with the database
        limit_per_minute: The maximum number of request per minute the database can send
    """

    db_name: str
    connector: type["CVEConnector"]
    limit_per_minute: int


class CVEDatabase(Enum):
    """An enumeration of CVE connectors."""

    NIST = CVEDatabaseProps(db_name="Nist", connector=NistConnector, limit_per_minute=10)
    CIRCL = CVEDatabaseProps(db_name="circl.lu", connector=CirclConnector, limit_per_minute=10)
    CVEORG = CVEDatabaseProps(db_name="CVE.org", connector=CVEorgConnector, limit_per_minute=10)

    @property
    def dbname(self) -> str:
        """
        Return the name of the CVE database.

        Returns:
            str: The name of the CVE database
        """

        return self._value_.db_name

    @property
    def connector(self) -> type["CVEConnector"]:
        """
        Return the connector property of a CVEDatabase.

        Returns:
            CVEConnector: the CVEConnector class of the CVEDatabase
        """

        return self._value_.connector

    @property
    def limit_per_minute(self) -> int:
        """
        Return the database request limit per minute.

        Returns:
            int: The maximum number of request per minute the database can send
        """

        return self._value_.limit_per_minute
