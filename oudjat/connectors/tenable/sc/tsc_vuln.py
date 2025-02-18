from typing import TYPE_CHECKING, Dict, List, Tuple, Union

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

        self.update({key: [] for key in TenableSCSeverity._member_names_})

    # ****************************************************************
    # Methods

    def get(self, *severities: List[str], key_exclude: List[str] = None) -> Dict:
        """Retreive the current vulnerabilities"""

        filters = [self.BUILTIN_FILTERS["exploitable"]]
        if severities is not None:
            filters.append(self.build_severity_filter(severities))

        if self.count(*severities) == 0:
            exploitable_vulns = self.search(*filters)
            self.add_vuln(exploitable_vulns)

        return {
            sev.upper(): [ self.clean_vuln(vuln=vuln, key_exclude=key_exclude) for vuln in self[sev.upper()] ]
            for sev in severities
        }

    def clean_vuln(self, vuln: Dict, key_exclude: List[str] = None) -> Dict:
        """Cleans a vuln of unwanted keys and line breaks if relevant"""
        return { 
            k: v.replace('\n', '') if type(v) is str else v
            for k,v in vuln.items() if key_exclude is None or k not in key_exclude
        }

    def get_unique(self, *severities: List[str]) -> Dict:
        """Returns a dictionary of unique vulnerabilities"""

        # Retreive all severities if none provided
        if severities is None:
            severities = TenableSCSeverity._member_names_

        # Retreives vulnerabilities vulnerabilities for the given severities if necessary
        if self.count(*severities) == 0:
            self.get(*severities)

        res = {}
        for sev in severities:
            sev_uniq_vuln = set()
            for vuln in self[sev.upper()]:
                sev_uniq_vuln.update(vuln["cve"].split(','))

            res[sev.upper()] = list(sev_uniq_vuln)

        return res

    def get_vulnerable_assets(self, *severities: List[str]) -> Dict:
        """Returns vulnerable assets for the given severities"""

        # Retreive all severities if none provided
        if severities is None:
            severities = TenableSCSeverity._member_names_

        # Retreives vulnerabilities vulnerabilities for the given severities if necessary
        if self.count(*severities) == 0:
            self.get(*severities)

        res = {}
        vuln_keys = ["pluginID", "pluginName", "description", "solution", "cvssV3BaseScore", "cve"]
        for sev in severities:
            for vuln in self[sev.upper()]:
                if vuln["uuid"] not in res.keys():
                    res[vuln["uuid"]] = {
                        "ip": vuln["ip"],
                        "dnsName": vuln["dnsName"],
                        "os": vuln["operatingSystem"],
                        "vulns": [],
                    }

                new_vuln = { k: v for k,v in vuln.items() if k in vuln_keys }
                new_vuln["severity"] = sev.upper()
                res[vuln["uuid"]]["vulns"].append(new_vuln)

        return res

    def count(self, *severities: List[str]) -> int:
        """Returns a number of vulnerabilities currently retreived based on provided severities"""

        # Retreive all severities if none provided
        if severities is None:
            severities = TenableSCSeverity._member_names_

        count = 0
        for sev in severities:
            if sev.upper() in TenableSCSeverity._member_names_:
                count += len(self[sev.upper()])

        return count

    def count_detailed(self, *severities: List[str]) -> Dict:
        """Returns the number of vulnerabilities per severity"""
        if severities is None:
            severities = TenableSCSeverity._member_names_

        return {sev: len(self[sev]) for sev in severities}

    def search(self, *search_filter: List[Tuple]) -> List:
        """Searches for vulns"""
        return list(self.tsc.analysis.vulns(*search_filter))

    def reset(self, *severities: List[str]) -> None:
        """Resets vulns list"""

        # Retreive all severities if none provided
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
            self[v["severity"]["name"].upper()].append(v)

    def build_severity_filter(self, *severities: List[str]) -> Tuple:
        """Returns a severity filter based on the provided severities"""
        sev_scores = ",".join([f"{TenableSCSeverity[sev].value}" for sev in list(*severities)])
        return "severity", "=", sev_scores
