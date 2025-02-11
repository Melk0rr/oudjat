from typing import TYPE_CHECKING, Dict, List, Tuple, Union

from .tsc_severities import TenableSCSeverity

if TYPE_CHECKING:
    from tenable.sc import TenableSC


class TenableSCVulns(dict):
    # ****************************************************************
    # Attributes & Constructors

    def __init__(self, tsc_connection: "TenableSC") -> None:
        """Constructor"""

        super().__init__()
        self.tsc = tsc_connection

        self.update({key: [] for key in TenableSCSeverity._member_names_})

    def get(self, *severities: List[str]) -> Dict:
        """Getter for the currently retreived vulnerabilities"""

        filters = [ self.BUILTIN_FILTERS["exploitable"] ]
        if severities is not None:
            filters += self.build_severity_filter(severities)

        if self.get_vuln_number() == 0:
            exploitable_vulns = self.search_vulns(*filters)
            self.add_vuln(exploitable_vulns)

        return { key: self.vulns[key] for key in severities }

    def reset(self, *severities: List[str]) -> None:
        """Resets vulns list"""
        if severities is None:
            severities = TenableSCSeverity._member_names_

        for sev in severities:
            if sev.upper() in TenableSCSeverity._member_names_:
                self.vulns[sev.upper()].clear()

    def add_vuln(self, vuln: Union[Dict, List[Dict]]) -> None:
        """Adds a vuln to the connector vuln dictionary"""
        if not isinstance(vuln, list):
            vuln = [vuln]

        for v in vuln:
            self.vulns[v["severity"]["name"].upper()] = v

    def build_severity_filter(self, *severities: List[str]) -> Tuple:
        """Returns a severity filter based on the provided severities"""
        return ("severity", "=", ','.join([ TenableSCSeverity[sev] for sev in severities ]))
