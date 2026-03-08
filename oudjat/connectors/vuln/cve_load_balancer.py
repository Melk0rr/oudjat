"""
A module to dynamically retrieve CVE data by switching between available APIs.
"""

import logging
import re
from time import sleep, time

from yaspin import yaspin

from oudjat.utils.context import Context
from oudjat.utils.logging import spinner_log
from oudjat.utils.types import DataType, StrType

from .cve_connector import CVEConnector
from .cve_databases import CVEDatabase
from .exceptions import CVEDatabaseConnectionError


class CVELoadBalancer:
    """
    A class to bypass CVE database APIs request / minute limitation.
    """

    # ****************************************************************
    # Attributes & Constructors

    def __init__(self) -> None:
        """
        Create a new instance of CVELoadBalancer.
        """

        self.logger: "logging.Logger" = logging.getLogger(__name__)

        self._pointer: int = 0
        self._apis: list["CVEConnector"] = [db.connector(db.limit_per_minute) for db in CVEDatabase]

    # ****************************************************************
    # Methods - helpers

    def _next_api(self) -> "CVEConnector | None":
        for _ in range(len(self._apis)):
            api = self._apis[self._pointer]
            self._pointer = (self._pointer + 1) % len(CVEDatabase)
            if api.token():
                return api

            return None

    def _time_to_wait(self) -> float:
        """
        Return the time the balancer must wait before one of its APIs is available again.

        Returns:
            float: Time to wait before a new API can be used
        """

        return min(api.rate - ((time() - api.last_token_time) * api.rate) for api in self._apis)

    # ****************************************************************
    # Methods - helpers

    def fetch(self, cves: "StrType") -> "DataType":
        """
        Fetch CVE data by dynamically switching between the available APIs.

        Auto switch between the APIs when one limit is reached.

        Args:
            cves (str | list[str]): A single CVE ID or a list of CVE IDs to be searched.

        Returns:
            DataType: A list of dictionaries containing filtered vulnerability information for each provided CVE ID.
        """

        context = Context()

        self.logger.info(f"{len(cves)} CVEs to resolve")
        self.logger.debug(f"{context}::{','.join([db.dbname for db in CVEDatabase])}")

        res = []
        with yaspin(text=f"Fetching CVE data from {len(self._apis)} APIs...") as spinner:
            for cve in cves:
                if not re.match(r"CVE-\d{4}-\d{4,7}", cve):
                    continue

                while True:
                    api = self._next_api()

                    if not api:
                        wait_time = max(self._time_to_wait(), 0.1)

                        spinner_log(
                            f"No API available, waiting {wait_time}...",
                            self.logger.warning,
                            spinner,
                        )

                        sleep(wait_time)
                        continue

                    spinner_log(f"Using {api.URL.netloc} for {cve}", self.logger.info, spinner)

                    cve_url = api.cve_api_url(cve)
                    try:
                        api.connect(cve_url)
                        vuln = api.vuln_from_connection()

                        if vuln:
                            spinner_log(f"{context}::{cve_url} > {vuln}", self.logger.debug, spinner)
                            res.append(api.unify_cve_data(vuln))
                            break

                        else:
                            spinner_log(
                                f"No data in {api.URL.netloc} for vulnerability {cve}",
                                self.logger.warning,
                                spinner,
                            )
                            continue

                    except CVEDatabaseConnectionError as e:
                        spinner.hide()
                        self.logger.error(e)
                        spinner.show()

                        continue

            if len(res) > 0:
                spinner.ok(f"✅ Retrieved data for {len(res)} CVEs")

            else:
                spinner.fail("❌ Could not retrieve any CVE data")

        return res
