"""A module that provides an easy CVE connectors hub."""

from enum import Enum
from typing import TYPE_CHECKING, NamedTuple

from .cveorg import CVEorgConnector
from .nist import NistConnector

if TYPE_CHECKING:
    from .cve_connector import CVEConnector


class CVEDatabaseProps(NamedTuple):
    """
    A helper clas to properly handle CVEDatabase property types.

    Attributes:
        db_name  : The name of the database
        connector: The connector associated with the database
    """

    db_name: str
    connector: type["CVEConnector"]


class CVEDatabase(Enum):
    """An enumeration of CVE connectors."""

    NIST = CVEDatabaseProps(db_name="Nist", connector=NistConnector)
    CVEORG = CVEDatabaseProps(db_name="CVE.org", connector=CVEorgConnector)

    @property
    def connector(self) -> type["CVEConnector"]:
        """
        Return the connector property of a CVEDatabase.

        Returns:
            CVEConnector: the CVEConnector class of the CVEDatabase
        """

        return self._value_.connector
