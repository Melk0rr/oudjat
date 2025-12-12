"""
A module to map EndOfLife.date results into actual assets.
"""

from oudjat.core.software import SoftwareReleaseSupport, SoftwareReleaseVersion
from oudjat.core.software.os.windows.windows import MSOSRelease

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

    def windows(self) -> dict[str, "MSOSRelease"]:
        """
        Return a dictionary of MSOSRelease instances.

        Returns:
            dict[str, MSOSRelease]: A dictionary of MSOSRelease for each windows instance retrieved from EOL API
        """

        releases: dict[str, "MSOSRelease"] = {}
        windows_eol = self._connector.windows()[0]
        software_name = " ".join(str(windows_eol["label"]).split(" ")[1:])

        for rel in windows_eol["releases"]:
            rel_version = rel["latest"]["name"]
            rel_name_split = str(rel["name"]).split("-")

            # Create release
            release_date = rel["releaseDate"]
            release_label = " ".join(str(rel["label"]).split(" ")[:2])

            releases[rel_version] = MSOSRelease(
                release_id=f"{windows_eol['name']}-{rel_version}",
                os_name=software_name,
                version=rel_version,
                release_date=release_date,
                release_label=release_label
            )

            releases[rel_version].latest_version = SoftwareReleaseVersion(rel_version)
            releases[rel_version].add_custom_attr("link", rel["latest"]["link"])

            # Handle support
            rel_channel = "-".join(rel_name_split[2:]).upper()
            rel_channel = ["E", "W"] if rel_channel == "" else [rel_channel]

            for ch in rel_channel:
                support = SoftwareReleaseSupport(
                    channel=ch,
                    active_support=rel["eoasFrom"],
                    security_support=rel["eolFrom"],
                    extended_security_support=rel["eoesFrom"],
                    long_term_support=rel["isLts"],
                )

                releases[rel_version].add_support(ch, support)

        return releases

    def windows_server(self) -> dict[str, "MSOSRelease"]:
        """
        Return a dictionary of MSOSRelease instances.

        Returns:
            dict[str, MSOSRelease]: A dictionary of MSOSRelease for each windows instance retrieved from EOL API
        """

        releases: dict[str, "MSOSRelease"] = {}
        windows_eol = self._connector.windows_server()[0]
        software_name = " ".join(str(windows_eol["label"]).split(" ")[1:])

        for rel in windows_eol["releases"]:
            rel_version = rel["latest"]["name"]
            rel_name_split = str(rel["name"]).split("-")

            # Create release
            release_date = rel["releaseDate"]
            release_label = str(rel["label"]).split(" ")[2]

            if "-sp" in rel["name"]:
                rel_version += rel_name_split[1]

            releases[rel_version] = MSOSRelease(
                release_id=f"{windows_eol['name']}-{rel_version}",
                os_name=software_name,
                version=rel_version,
                release_date=release_date,
                release_label=release_label
            )

            releases[rel_version].latest_version = SoftwareReleaseVersion(rel_version)
            releases[rel_version].add_custom_attr("link", rel["latest"]["link"])

            # Handle support
            rel_channel = "-".join(rel_name_split[1:]).upper()
            rel_channel = ["LTSC"] if rel_channel == "" else [rel_channel]

            for ch in rel_channel:
                support = SoftwareReleaseSupport(
                    channel=ch,
                    active_support=rel["eoasFrom"],
                    security_support=rel["eolFrom"],
                    extended_security_support=rel["eoesFrom"],
                    long_term_support=rel["isLts"],
                )

                releases[rel_version].add_support(ch, support)

        return releases
