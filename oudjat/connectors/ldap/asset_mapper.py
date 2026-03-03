"""
A module that handle LDAP entry mapping to asset elements.
"""

import logging
from typing import TYPE_CHECKING, Any

from oudjat.connectors.mapping_functions import MappingFunction
from oudjat.core.computer.computer import Computer
from oudjat.core.software.os.operating_system import OSReleaseListFilter
from oudjat.core.user.user import User
from oudjat.utils.types import DataType

from ..asset_mapper import AssetMapper, MappingOSTuple
from .ldap_connector import LDAPConnector

if TYPE_CHECKING:
    from oudjat.core.mapper import MappingRegistry


class LDAPAssetMapper(AssetMapper):
    """
    A class that maps LDAPEntry instances into various assets.
    """

    # ****************************************************************
    # Attributes & Constructor

    def __init__(self, ldapco: "LDAPConnector") -> None:
        """
        Create a new LDAPAssetMapper.

        Args:
            ldapco (LDAPConnector): The LDAP connector used to interact with LDAP server
        """

        super().__init__()
        self.logger: "logging.Logger" = logging.getLogger(__name__)

        self._connector: "LDAPConnector" = ldapco

    # ****************************************************************
    # Methods - Asset mapping

    ### Computer mappping
    def computers(
        self, entries: "DataType", mapping_registry: "MappingRegistry | None" = None
    ) -> dict[str, "Computer"]:
        """
        Map LDAP entries into Computer instances.

        You can specify a custom mapping registry. By default, the mapping registry is:
            "computer_id": "id"
            "name": "name"
            "description": "description"
            "label": "hostname"

        Args:
            entries (list[LDAPEntry])                : Entries to map
            mapping_registry (MappingRegistry | None): Optional mapping registry

        Returns:
            dict[str, Computer]: A dictionary of Computer instances
        """

        self.logger.info(f"Mapping {len(entries)} LDAP entries into Computer asset")

        if mapping_registry is None:
            mapping_registry = {
                "computer_id": lambda c: c["id"],
                "name": lambda c: c["name"],
                "description": lambda c: c["description"],
                "label": lambda c: c["hostname"],
            }

        def asset_cb(asset: "Computer", record: dict[str, Any], _: "MappingRegistry") -> None:
            release_filters: list["OSReleaseListFilter"] = [
                lambda rl: rl.filter_max_version(),
                lambda rl: rl.filter_by_label(record["os"]["name"]),
            ]

            os: "MappingOSTuple" = MappingFunction.OS(
                func="os_details_from_str",
                os_str=record["os"]["name"],
                os_ver=record["os"]["version"],
                filters=release_filters,
            )

            os_instance, os_rel, os_edition = os
            if os_instance is not None:
                asset.computer_type = next(iter(os_instance.computer_type))

            asset.os_release = os_rel
            asset.os_edition = os_edition

            asset.flags.update(record["flags"])
            record.pop("flags", None)

            asset.add_custom_attr("ldap", record)

        return self.map_many(
            records=entries,
            map_cls=Computer,
            mapping_registry=mapping_registry,
            asset_cb=asset_cb,
            key_cb=lambda r: r["dn"],
        )

    ### User mappping
    def users(
            self, entries: "DataType", mapping_registry: "MappingRegistry | None" = None
    ) -> dict[str, "User"]:
        """
        Map LDAP entries into User instances.

        You can specify a custom mapping registry. By default, the mapping registry is:
            "user_id": "user_id"
            "name": "name"
            "login": "san"
            "firstname": "givenname"
            "lastname": "surname"
            "email": "email"

        Args:
            entries (list[LDAPEntry])                : Entries to map
            mapping_registry (MappingRegistry | None): Optional mapping registry that will replace the default one to map Computers

        Returns:
            dict[str, Computer]: A dictionary of User instances
        """

        if mapping_registry is None:
            mapping_registry = {
                "user_id": lambda u: u["id"],
                "name": lambda u: u["name"],
                "login": lambda u: u["san"],
                "firstname": lambda u: u["givenname"],
                "lastname": lambda u: u["surname"],
                "email": lambda u: u["email"],
            }

        def asset_cb(asset: "User", record: dict[str, Any], _: "MappingRegistry") -> None:
            asset.flags.update(record["flags"])
            record.pop("flags", None)

            asset.add_custom_attr("ldap", record)

        return self.map_many(
            records=entries,
            map_cls=User,
            mapping_registry=mapping_registry,
            asset_cb=asset_cb,
            key_cb=lambda r: r["id"]
        )
