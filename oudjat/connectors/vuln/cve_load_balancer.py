"""
A module to dynamically retrieve CVE data by switching between available APIs.
"""

import logging
import re
from time import sleep
from typing import Any

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

        return min(api.time_to_wait() for api in self._apis)

    # ****************************************************************
    # Methods - helpers

    def fetch(
        self,
        cves: "StrType",
        payload: dict[str, Any] | None = None,
    ) -> "DataType":
        """
        Fetch CVE data by dynamically switching between the available APIs.

        Auto switch between the APIs when one limit is reached.

        Args:
            cves (str | list[str])         : A single CVE ID or a list of CVE IDs to be searched.
            payload (dict[str, Any] | None): Payload to send to the target CVE API url

        Returns:
            DataType: A list of dictionaries containing filtered vulnerability information for each provided CVE ID.
        """

        context = Context()

        if payload is None:
            payload = {}

        self.logger.info(f"{len(cves)} CVEs to resolve")
        self.logger.debug(f"{context}::{','.join([db.dbname for db in CVEDatabase])}")

        res = []
        spinner_txt = f"Fetching CVE data from {len(self._apis)} APIs"
        with yaspin(text=f"{spinner_txt}...") as spinner:
            for i, cve in enumerate(cves):
                spinner.text = f"{spinner_txt} ({i+1}/{len(cves)})..."

                if not re.match(r"CVE-\d{4}-\d{4,7}", cve):
                    continue

                api_count = 0

                while True:
                    api = self._next_api()

                    if not api:
                        wait_time = self._time_to_wait()

                        spinner_log(
                            f"No API available, waiting {round(wait_time, ndigits=2)}s...",
                            self.logger.warning,
                            spinner,
                        )

                        sleep(wait_time)
                        continue

                    api_count += 1
                    spinner_log(f"Using {api.URL.netloc} for {cve}", self.logger.info, spinner)

                    cve_url = api.cve_api_url(cve)
                    try:
                        api.connect(cve_url, **payload)
                        vuln = api.vuln_from_connection()

                        if vuln:
                            spinner_log(
                                f"{context}::{cve_url} > {vuln}", self.logger.debug, spinner
                            )
                            res.append(api.unify_cve_data(vuln))
                            break

                        else:
                            spinner_log(
                                f"No data in {api.URL.netloc} for vulnerability {cve}",
                                self.logger.warning,
                                spinner,
                            )

                            if api_count == len(self._apis):
                                break

                            continue

                    except CVEDatabaseConnectionError as e:
                        spinner_log(f"{e}", self.logger.error, spinner)
                        continue

            if len(res) > 0:
                spinner.text = f"Retrieved data for {len(res)} CVEs"
                spinner.ok("✅ ")

            else:
                spinner.fail("❌ ")

        return res
