"""
A module to map EndOfLife.date results into actual assets.
"""

import re

from oudjat.core.software import SoftwareReleaseSupport, SoftwareReleaseVersion
from oudjat.core.software.os import OSRelease

from ..asset_mapper import AssetMapper, MappingRegistry
from .eol_connector import EndOfLifeConnector


class EOLAssetMapper(AssetMapper):
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

        super().__init__()

        self._connector: "EndOfLifeConnector" = eolco

    # ****************************************************************
    # Methods

    def windows(self) -> dict[str, list["OSRelease"]]:
        """
        Return a dictionary of MSOSRelease instances.

        Returns:
            dict[str, list[OSRelease]]: A dictionary of OSRelease for each windows instance retrieved from EOL API
        """

        releases: dict[str, list["OSRelease"]] = {}
        windows_eol = self._connector.windows()[0]
        software_name = " ".join(str(windows_eol["label"]).split(" ")[1:])


        def rel_label(label: str) -> str | None:
            label_split = label.split(" ")
            return label_split[1] if len(label_split) >= 2 else None

        mapping_registry: "MappingRegistry" = {
            "release_id": ("latest", lambda latest: f"{windows_eol['name']}{latest['name']}"),
            "name": ("label", lambda label: f"{software_name} {label.split(' ')[0]}"),
            "software_name": lambda _: software_name,
            "version": ("latest", lambda latest: latest["name"]),
            "release_date": "releaseDate",
            "release_label": ("label", lambda label: rel_label(label))
        }

        # TODO: Finish AssetMapper implementation + find a way to handle conditional map

        for rel in windows_eol["releases"]:
            rel_version = rel["latest"]["name"]
            rel_name_split = str(rel["name"]).split("-")

            # Create release
            release_date = rel["releaseDate"]
            rel_label_split = str(rel["label"]).split(" ")
            release_label = rel_label_split[1] if len(rel_label_split) >= 2 else None

            rel_key = rel_version
            rel_id = f"{windows_eol['name']}-{rel_version}"

            if rel_key not in releases.keys():
                releases[rel_key] = []

            # If element with the same id already exist. Then don't add a new release
            exist = next((i for i, el in enumerate(releases[rel_key]) if el.id == rel_id), None)
            index = 0

            if exist is None:
                os_rel = OSRelease(
                    release_id=rel_id,
                    name=f"{software_name} {rel['label'].split(' ')[0]}",
                    software_name=software_name,
                    version=rel_version,
                    release_date=release_date,
                    release_label=release_label,
                )

                os_rel.latest_version = SoftwareReleaseVersion(rel_version)
                os_rel.add_custom_attr("link", rel["latest"]["link"])

                releases[rel_key].append(os_rel)

            else:
                index = exist

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

                releases[rel_key][index].add_support(ch, support)

        return releases

    def windows_server(self) -> dict[str, list["OSRelease"]]:
        """
        Return a dictionary of MSOSRelease instances.

        Returns:
            dict[str, list[OSRelease]]: A dictionary of OSRelease for each windows instance retrieved from EOL API
        """

        releases: dict[str, list["OSRelease"]] = {}
        windows_eol = self._connector.windows_server()[0]
        software_name = " ".join(str(windows_eol["label"]).split(" ")[1:])

        for rel in windows_eol["releases"]:
            rel_version = rel["latest"]["name"]
            rel_name_split = str(rel["name"]).split("-")

            # Create release
            release_date = rel["releaseDate"]
            release_label = (
                " ".join(str(rel["label"]).split(" ")[2:])
                .replace(" (LTSC)", "")
                .replace(" SAC", "")
                .replace(" AC", "")
            )

            rel_key = rel_version

            if "-sp" in rel["name"]:
                rel_version += rel_name_split[1]

            rel_id = f"{windows_eol['name']}-{release_label.replace(' ', '-')}-{rel_version}"

            if rel_key not in releases.keys():
                releases[rel_key] = []

            # If element with the same id already exist. Then don't add a new release
            exist = next((i for i, el in enumerate(releases[rel_key]) if el.id == rel_id), None)
            index = 0

            if exist is None:
                os_rel = OSRelease(
                    release_id=rel_id,
                    name=f"{software_name} {rel_name_split[0]}",
                    software_name=software_name,
                    version=rel_version,
                    release_date=release_date,
                    release_label=release_label,
                )

                os_rel.latest_version = SoftwareReleaseVersion(rel_version)
                os_rel.add_custom_attr("link", rel["latest"]["link"])

                releases[rel_key].append(os_rel)

            else:
                index = exist

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

                releases[rel_key][index].add_support(ch, support)

        return releases

    def rhel(self) -> dict[str, list["OSRelease"]]:
        """
        Return a dictionary of MSOSRelease instances.

        Returns:
            dict[str, list[OSRelease]]: A dictionary of OSRelease for each windows instance retrieved from EOL API
        """

        releases: dict[str, list["OSRelease"]] = {}
        rhel_eol = self._connector.products("rhel")[0]
        software_name = rhel_eol["label"]

        for rel in rhel_eol["releases"]:
            rel_version = SoftwareReleaseVersion(int(rel["name"]))
            rel_key = f"{rel_version.major}"

            # Create release
            release_date = rel["releaseDate"]
            release_label = rel["name"]

            os_rel = OSRelease(
                release_id=f"{rhel_eol['name']}-{rel['name']}",
                name=f"{software_name} {rel['name']}",
                software_name=software_name,
                version=str(rel_version),
                release_date=release_date,
                release_label=release_label,
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
