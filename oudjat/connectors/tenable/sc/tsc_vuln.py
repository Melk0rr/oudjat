from typing import TYPE_CHECKING, Dict, List, Tuple, Union

from .tsc_severities import TenableSCSeverity

if TYPE_CHECKING:
    from tenable.sc import TenableSC


class TenableSCVulns(dict):
    # ****************************************************************
    # Attributes & Constructors

    BUILTIN_FILTERS = {
        "exploitable": ("exploitAvailable", "=", "true")
    }

    def __init__(self, tsc_connection: "TenableSC") -> None:
        """Constructor"""

        super().__init__()
        self.tsc = tsc_connection

        self.update({key: [] for key in TenableSCSeverity._member_names_})

    # ****************************************************************
    # Methods

    def get(self, *severities: List[str]) -> Dict:
        """Getter for the currently retreived vulnerabilities"""

        filters = [ self.BUILTIN_FILTERS["exploitable"] ]
        if severities is not None:
            filters += self.build_severity_filter(severities)

        if self.count() == 0:
            exploitable_vulns = self.search_vulns(*filters)
            self.add_vuln(exploitable_vulns)

        return { key: self.vulns[key] for key in severities }

    def count(self, *severities: List[str]) -> int:
        """Returns a number of vulnerabilities currently retreived based on provided severities"""
        if severities is None:
            severities = TenableSCSeverity._member_names_

        count = 0
        for sev in severities:
            if sev.upper() in TenableSCSeverity._member_names_:
                count += len(self[sev.upper()])

        return count

    def search(self, *search_filter: List[Tuple]) -> List:
        """Searches for vulns"""
        search = self.tsc.analysis.vuln(search_filter)
        return list(search)

    def reset(self, *severities: List[str]) -> None:
        """Resets vulns list"""
        if severities is None:
            severities = TenableSCSeverity._member_names_

        for sev in severities:
            if sev.upper() in TenableSCSeverity._member_names_:
                self[sev.upper()].clear()

    def add_vuln(self, vuln: Union[Dict, List[Dict]]) -> None:
        """Adds a vuln to the connector vuln dictionary"""
        if not isinstance(vuln, list):
            vuln = [vuln]

        for v in vuln:
            self[v["severity"]["name"].upper()] = v

    def build_severity_filter(self, *severities: List[str]) -> Tuple:
        """Returns a severity filter based on the provided severities"""
        sev_scores = ','.join([ f"{TenableSCSeverity[sev].value}" for sev in list(*severities) ])
        return ("severity", "=", sev_scores)
