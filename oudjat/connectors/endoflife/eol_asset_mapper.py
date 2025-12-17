"""
A module to map EndOfLife.date results into actual assets.
"""

import re

from oudjat.core.software import SoftwareReleaseSupport, SoftwareReleaseVersion
from oudjat.core.software.os import OSRelease

from .eol_connector import EndOfLifeConnector


class EOLAssetMapper:
    """
    A class that maps LDAPEntry instances into various assets.
    """

    # ****************************************************************
    # Attributes & Constructor

    def __init__(self, eolco: "EndOfLifeConnector") -> None:
        """
        Create a new EOL asset mapper.

        Args:
            eolco (EndOfLifeConnector): The connector used to interact with endoflife.date API
        """

        self._connector: "EndOfLifeConnector" = eolco

    # ****************************************************************
    # Methods

    def windows(self) -> dict[str, list["OSRelease"]]:
        """
        Return a dictionary of MSOSRelease instances.

        Returns:
            dict[str, MSOSRelease]: A dictionary of MSOSRelease for each windows instance retrieved from EOL API
        """

        releases: dict[str, list["OSRelease"]] = {}
        windows_eol = self._connector.windows()[0]
        software_name = " ".join(str(windows_eol["label"]).split(" ")[1:])

        for rel in windows_eol["releases"]:
            rel_version = rel["latest"]["name"]
            rel_name_split = str(rel["name"]).split("-")

            # Create release
            release_date = rel["releaseDate"]
            rel_label_split = str(rel["label"]).split(" ")
            release_label = rel_label_split[1] if len(rel_label_split) >= 2 else None

            rel_key = rel_version
            os_rel = OSRelease(
                release_id=f"{windows_eol['name']}-{rel_version}",
                name=f"{software_name} {rel['label'].split(" ")[0]}",
                os_name=software_name,
                version=rel_version,
                release_date=release_date,
                release_label=release_label
            )

            os_rel.latest_version = SoftwareReleaseVersion(rel_version)
            os_rel.add_custom_attr("link", rel["latest"]["link"])

            # Handle support
            rel_channel = "-".join(rel_name_split[2:]).upper()
            rel_channel = ["E", "W"] if rel_channel == "" else [rel_channel]

            for ch in rel_channel:
                support = SoftwareReleaseSupport(
                    channel=ch,
                    support_from=release_date,
                    active_support=rel["eoasFrom"],
                    security_support=rel["eolFrom"],
                    extended_security_support=rel["eoesFrom"],
                    long_term_support=rel["isLts"],
                )

                os_rel.add_support(ch, support)

            if rel_key not in releases.keys():
                releases[rel_key] = []

            releases[rel_key].append(os_rel)

        return releases

    def windows_server(self) -> dict[str, list["OSRelease"]]:
        """
        Return a dictionary of MSOSRelease instances.

        Returns:
            dict[str, MSOSRelease]: A dictionary of MSOSRelease for each windows instance retrieved from EOL API
        """

        releases: dict[str, list["OSRelease"]] = {}
        windows_eol = self._connector.windows_server()[0]
        software_name = " ".join(str(windows_eol["label"]).split(" ")[1:])

        for rel in windows_eol["releases"]:
            rel_version = rel["latest"]["name"]
            rel_name_split = str(rel["name"]).split("-")

            # Create release
            release_date = rel["releaseDate"]
            release_label = " ".join(str(rel["label"]).split(" ")[2:]).replace(" (LTSC)", "").replace(" SAC", "").replace(" AC", "")

            rel_key = rel_version

            if "-sp" in rel["name"]:
                rel_version += rel_name_split[1]

            os_rel = OSRelease(
                release_id=f"{windows_eol['name']}-{release_label.replace(' ', '-')}-{rel_version}",
                name=f"{software_name} {rel_name_split[0]}",
                os_name=software_name,
                version=rel_version,
                release_date=release_date,
                release_label=release_label
            )

            os_rel.latest_version = SoftwareReleaseVersion(rel_version)
            os_rel.add_custom_attr("link", rel["latest"]["link"])

            # Handle support
            channel_search = re.search(r"(LTSC|SAC|AC)", rel["label"])
            rel_channel = [channel_search.group(0)] if channel_search is not None else ["LTSC"]

            for ch in rel_channel:
                support = SoftwareReleaseSupport(
                    channel=ch,
                    support_from=release_date,
                    active_support=rel["eoasFrom"],
                    security_support=rel["eolFrom"],
                    extended_security_support=rel["eoesFrom"],
                    long_term_support=rel["isLts"],
                )

                os_rel.add_support(ch, support)

            if rel_key not in releases.keys():
                releases[rel_key] = []

            releases[rel_key].append(os_rel)

        return releases

    def rhel(self) -> dict[str, list["OSRelease"]]:
        """
        Return a dictionary of MSOSRelease instances.

        Returns:
            dict[str, MSOSRelease]: A dictionary of MSOSRelease for each windows instance retrieved from EOL API
        """

        releases: dict[str, list["OSRelease"]] = {}
        rhel_eol = self._connector.products("rhel")[0]
        software_name = rhel_eol["label"]

        for rel in rhel_eol["releases"]:
            rel_version = SoftwareReleaseVersion(int(rel["name"]))
            rel_key = str(rel_version)

            # Create release
            release_date = rel["releaseDate"]
            release_label = rel["name"]

            os_rel = OSRelease(
                release_id=f"{rhel_eol['name']}-{rel_version}",
                name=f"{software_name} {rel['name']}",
                os_name=software_name,
                version=str(rel_version),
                release_date=release_date,
                release_label=release_label
            )

            os_rel.latest_version = SoftwareReleaseVersion(rel["latest"]["name"])
            os_rel.add_custom_attr("link", rel["latest"]["link"])

            # Handle support
            for ch in ["Standard", "ELS"]:
                support = SoftwareReleaseSupport(
                    channel=ch,
                    support_from=release_date if ch == "Standard" else rel["eolFrom"],
                    active_support=rel["eoasFrom"] if ch == "Standard" else rel["eoesFrom"],
                    security_support=rel["eolFrom"] if ch == "Standard" else rel["eoesFrom"],
                    extended_security_support=rel["eoesFrom"] if ch == "ELS" else None,
                    long_term_support=rel["isLts"],
                )

                os_rel.add_support(ch, support)

            if rel_key not in releases.keys():
                releases[rel_key] = []

            releases[rel_key].append(os_rel)

        return releases
