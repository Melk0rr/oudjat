from typing import TYPE_CHECKING, Dict, List, Tuple

from .tsc_severities import TenableSCSeverity

if TYPE_CHECKING:
    from tenable.sc import TenableSC


class TenableSCVulns(dict):
    # ****************************************************************
    # Attributes & Constructors

    BUILTIN_FILTERS = {"exploitable": ("exploitAvailable", "=", "true")}

    def __init__(self, tsc_connection: "TenableSC") -> None:
        """Constructor"""

        super().__init__()
        self.tsc = tsc_connection

    # ****************************************************************
    # Methods

    def search(
        self, *severities: List[str], key_exclude: List[str] = None, tool: str = "vulndetails"
    ) -> Dict:
        """Retreive the current vulnerabilities"""

        filters = [self.BUILTIN_FILTERS["exploitable"]]
        if severities is not None:
            filters.append(self.build_severity_filter(severities))

        search = self.tsc.analysis.vulns(*filters, tool=tool)
        return list(search)

    def build_severity_filter(self, *severities: List[str]) -> Tuple:
        """Returns a severity filter based on the provided severities"""
        sev_scores = ",".join([f"{TenableSCSeverity[sev].value}" for sev in list(*severities)])
        return "severity", "=", sev_scores
