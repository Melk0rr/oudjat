"""
A module to map EndOfLife.date results into actual assets.
"""

from oudjat.core.software import SoftwareReleaseSupport, SoftwareReleaseVersion
from oudjat.core.software.os import OSRelease
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
        software_name = str(windows_eol["name"]).capitalize()

        for rel in windows_eol["releases"]:
            rel_version = rel["latest"]["name"]
            rel_name_split = str(rel["name"]).split("-")

            if rel_version not in releases.keys():
                release_date = rel["releaseDate"]
                release_label = " ".join(rel_name_split[:2]).upper()

                releases[rel_version] = MSOSRelease(
                    os_name=software_name,
                    version=rel_version,
                    release_date=release_date,
                    release_label=release_label
                )

                releases[rel_version].latest_version = SoftwareReleaseVersion(rel_version)
                releases[rel_version].add_custom_attr("link", rel["latest"]["link"])

            rel_channel = "-".join(rel_name_split[2:]).upper()
            support = SoftwareReleaseSupport(
                channel=rel_channel,
                active_support=rel["eoasFrom"],
                security_support=rel["eolFrom"],
                extended_security_support=rel["eoesFrom"],
                long_term_support=rel["isLts"],
            )

            releases[rel_version].add_support(rel_channel, support)

        return releases
