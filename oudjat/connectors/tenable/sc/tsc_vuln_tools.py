"""A simple module to list Tenable.sc vulnerability tools."""

from enum import Enum
from typing import override


class TSCVulnTool(Enum):
    """Enumeration of Tenable SC vulnerability tools."""

    CCEIPDETAIL           = "cceipdetail"
    CVEIPDETAIL           = "cveipdetail"
    IAVMIPDETAIL          = "iavmipdetail"
    IPLIST                = "iplist"
    LISTMAILCLIENTS       = "listmailclients"
    LISTSERVICES          = "listservices"
    LISTOS                = "listos"
    LISTSOFTWARE          = "listsoftware"
    LISTSSHSERVERS        = "listsshservers"
    LISTVULN              = "listvuln"
    LISTWEBCLIENTS        = "listwebclients"
    LISTWEBSERVERS        = "listwebservers"
    SUMASSET              = "sumasset"
    SUMCCE                = "sumcce"
    SUMCLASSA             = "sumclassa"
    SUMCLASSB             = "sumclassb"
    SUMCLASSC             = "sumclassc"
    SUMCVE                = "sumcve"
    SUMDNSNAME            = "sumdnsname"
    SUMFAMILY             = "sumfamily"
    SUMIAVM               = "sumiavm"
    SUMID                 = "sumid"
    SUMIP                 = "sumip"
    SUMMSBULLETIN         = "summsbulletin"
    SUMPROTOCOL           = "sumprotocol"
    SUMREMEDIATION        = "sumremediation"
    SUMSEVERITY           = "sumseverity"
    SUMUSERRESPONSIBILITY = "sumuserresponsibility"
    SUMPORT               = "sumport"
    TREND                 = "trend"
    VULNDETAILS           = "vulndetails"
    VULNIPDETAIL          = "vulnipdetail"
    VULNIPSUMMARY         = "vulnipsummary"
    SUMWASURL             = "sumwasurl"
    WASVULNDETAIL         = "wasvulndetail"
    WASLISTVULN           = "waslistvuln"

    @override
    def __str__(self) -> str:
        """
        Convert the vulnerability tool into a string.

        Returns:
            str: A string representation of the vulnerability tool
        """

        return self._value_
