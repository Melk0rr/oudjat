"""A module that provides an easy CVE connectors hub."""

from enum import Enum
from typing import TYPE_CHECKING

from .cveorg import CVEorgConnector
from .nist import NistConnector

if TYPE_CHECKING:
    from .cve_connector import CVEConnector

class CVEDatabase(Enum):
    """An enumeration of CVE connectors."""

    NIST = { "db_name": "Nist" , "connector": NistConnector }
    CVEORG = { "db_name": "CVE.org", "connector": CVEorgConnector }

    @property
    def connector(self) -> "CVEConnector":
        """
        Return the connector property of a CVEDatabase.

        Returns:
            CVEConnector: the CVEConnector class of the CVEDatabase
        """

        return self._value_["connector"]
