"""
A module to map EndOfLife.date results into actual assets.
"""

import re
from typing import Any, TypedDict

from oudjat.connectors.asset_mapper import AssetMapper, AssetMappingCallback
from oudjat.core.mapper import (
    Mapper,
    MappingRegistry,
    MappingValue,
)
from oudjat.core.software import (
    SoftwareReleaseVersion,
    Support,
    SupportPhase,
    SupportPhaseType,
)
from oudjat.core.software.os import OSRelease
from oudjat.core.software.software_release import ReleaseType, SoftwareRelVersionDict

from .eol_connector import EndOfLifeConnector


class SupportPhaseLabelsProps(TypedDict):
    """
    A simple class to describe properties expected in endoflife.date support phase labels.
    """

    eoas: str | None
    discontinued: str | None
    eol: str | None
    eoes: str | None


class EOLAssetMapper(AssetMapper):
    """
    A class that maps LDAPEntry instances into various assets.
    """

    # ****************************************************************
    # Attributes & Constructor

    def __init__(self) -> None:
        """
        Create a new EOL asset mapper.

        Args:
            eolco (EndOfLifeConnector): The connector used to interact with endoflife.date API
        """

        super().__init__()

        self._connector: EndOfLifeConnector = EndOfLifeConnector()
        self._connector.connect()

    # ****************************************************************
    # Methods

    def _map_support_dict(
        self, release: dict[str, Any], labels: "SupportPhaseLabelsProps"
    ) -> Support:
        label_sphase_map = {
            "eoas": "ACTIVE_SUPPORT",
            "eol": "SECURITY_SUPPORT",
            "eoes": "EXTENDED_SUPPORT",
        }

        sd = Support()
        start = release["releaseDate"]
        for lk, l in labels.items():
            end_key = f"{lk}From"
            if lk == "discontinued" or l is None or release.get(end_key, None) is None:
                continue

            phase_type: str = label_sphase_map[lk]
            end: str = release[end_key]

            sd.add(
                SupportPhase(
                    SupportPhaseType[phase_type],
                    start,
                    end,
                    str(l),
                )
            )

            start = end

        return sd

    def _releases(
        self,
        product: dict[str, Any],
        rel_type: type["ReleaseType"],
        mapping_registry: "MappingRegistry",
        callback: "AssetMappingCallback | None" = None,
        support_channels: "MappingValue | None" = None,
    ) -> "SoftwareRelVersionDict[ReleaseType]":

        releases = product.get("releases", [])
        final_releases = SoftwareRelVersionDict()

        def _support_assign_cb(
            ch: str, s: "Support", rel_ver: str, index: int | None
        ) -> None:
            final_releases[rel_ver][index or 0].add_support(ch, s)

        for rel in releases:
            rel_ver = Mapper.decapsulate_value(mapping_registry["version"], rel)
            rel_id = Mapper.decapsulate_value(mapping_registry["release_id"], rel)

            # Map the releases
            index = final_releases.find_unique_index(rel_ver, rel_id)
            if index is None:
                rel_instance = self.map_one(
                    record=rel,
                    map_cls=rel_type,
                    mapping_registry=mapping_registry,
                    callback=callback,
                )

                final_releases.add(rel_ver, rel_instance)

            # Add support to the releases
            mapped_channels = Mapper.decapsulate_value(support_channels, rel)
            for ch in mapped_channels or ["Standard"]:
                _support_assign_cb(ch, self._map_support_dict(rel, product["labels"]),rel_ver, index)

        return final_releases

    def windows(self) -> "SoftwareRelVersionDict[OSRelease]":
        """
        Return a dictionary of MSOSRelease instances.

        Returns:
            dict[str, list[OSRelease]]: A dictionary of OSRelease for each windows instance retrieved from EOL API
        """

        windows_eol = self._connector.windows()[0]
        software_name = " ".join(str(windows_eol["label"]).split(" ")[1:])

        def rel_label(rel: dict[str, Any]) -> str | None:
            label_split = rel["label"].split(" ")
            return label_split[1] if len(label_split) >= 2 else None

        mapping_registry: MappingRegistry = {
            "release_id": lambda rel: f"{windows_eol['name']}{rel['latest']['name']}",
            "name": lambda rel: f"{software_name} {rel['label'].split(' ')[0]}",
            "software": software_name,
            "version": lambda rel: rel["latest"]["name"],
            "release_date": lambda rel: rel["releaseDate"],
            "release_label": rel_label,
        }

        def rel_cb(
            rel: "OSRelease", record: dict[str, Any], _: "MappingRegistry"
        ) -> None:
            rel.add_custom_attr("link", record["latest"]["link"])

        def support_channels_value(rel: dict[str, Any]) -> list[str]:
            rel_name_split = str(rel["name"]).split("-")
            rel_channel = "-".join(rel_name_split[2:]).upper()

            return ["E", "W"] if rel_channel == "" else [rel_channel]

        return self._releases(
            product=windows_eol,
            rel_type=OSRelease,
            mapping_registry=mapping_registry,
            callback=rel_cb,
            support_channels=support_channels_value,
        )

    def windows_server(self) -> "SoftwareRelVersionDict[OSRelease]":
        """
        Return a dictionary of MSOSRelease instances.

        Returns:
            dict[str, list[OSRelease]]: A dictionary of OSRelease for each windows instance retrieved from EOL API
        """

        windows_eol = self._connector.windows_server()[0]
        software_name = " ".join(str(windows_eol["label"]).split(" ")[1:])

        def rel_label(rel: dict[str, Any]) -> str:
            return (
                " ".join(str(rel["label"]).split(" ")[2:])
                .replace(" (LTSC)", "")
                .replace(" SAC", "")
                .replace(" AC", "")
            )

        def rel_ver(rel: dict[str, Any]) -> str:
            rel_version = rel["latest"]["name"]
            if "-sp" in rel["name"]:
                rel_version += rel["name"].split("-")[1]

            return rel_version

        mapping_registry: MappingRegistry = {
            "release_id": lambda rel: (
                f"{windows_eol['name']}-{rel_label(rel).replace(' ', '-')}-{rel_ver(rel)}"
            ),
            "name": lambda rel: f"{software_name} {rel['name'].split('-')[0]}",
            "software": software_name,
            "version": rel_ver,
            "release_date": lambda rel: rel["releaseDate"],
            "release_label": rel_label,
        }

        def rel_cb(
            rel: "OSRelease", record: dict[str, Any], _: "MappingRegistry"
        ) -> None:
            rel.add_custom_attr("link", record["latest"]["link"])

        def support_channels_value(rel: dict[str, Any]) -> list[str]:
            channel_search = re.search(r"(LTSC|SAC|AC)", rel["label"])
            return [channel_search.group(0)] if channel_search is not None else ["LTSC"]

        return self._releases(
            product=windows_eol,
            rel_type=OSRelease,
            mapping_registry=mapping_registry,
            callback=rel_cb,
            support_channels=support_channels_value,
        )

    def linux(self, distro: str) -> "SoftwareRelVersionDict[OSRelease]":
        """
        Return a dictionary of MSOSRelease instances.

        Args:
            distro (str): The name of the distribution you want to retrieve

        Returns:
            dict[str, list[OSRelease]]: A dictionary of OSRelease for each windows instance retrieved from EOL API
        """

        distro_eol = self._connector.products(distro)[0]
        software_name = distro_eol["label"]

        mapping_registry: MappingRegistry = {
            "release_id": lambda rel: f"{distro_eol['name']}-{rel['name']}",
            "name": lambda rel: f"{software_name} {rel['name']}",
            "software": software_name,
            "version": lambda rel: str(SoftwareReleaseVersion(float(rel["name"]))),
            "release_date": lambda rel: rel["releaseDate"],
            "release_label": lambda rel: rel["name"],
        }

        def rel_cb(
            rel: "OSRelease", record: dict[str, Any], _: "MappingRegistry"
        ) -> None:
            if "latest" in record and record["latest"] is not None:
                rel.latest_version = SoftwareReleaseVersion(record["latest"]["name"])
                rel.add_custom_attr("link", record["latest"]["link"])

        return self._releases(
            product=distro_eol,
            rel_type=OSRelease,
            mapping_registry=mapping_registry,
            callback=rel_cb,
            support_channels=["Standard"],
        )
