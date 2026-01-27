"""
A module that handle LDAP entry mapping to asset elements.
"""

import logging
from typing import TYPE_CHECKING, Any

from oudjat.connectors.mapping_functions import MappingFunction
from oudjat.core.computer.computer import Computer
from oudjat.core.software.os.operating_system import OSReleaseListFilter
from oudjat.utils import Context

from ..asset_mapper import AssetMapper, MappingOSTuple
from .ldap_connector import LDAPConnector
from .objects.account.group.ldap_group import LDAPGroup
from .objects.account.ldap_computer import LDAPComputer
from .objects.account.ldap_user import LDAPUser
from .objects.gpo.ldap_gpo import LDAPGroupPolicyObject
from .objects.ldap_entry import LDAPEntry
from .objects.ldap_object import LDAPCapabilities, LDAPObject, LDAPObjectOptions
from .objects.ldap_object_types import LDAPObjectType
from .objects.ou.ldap_ou import LDAPOrganizationalUnit
from .objects.subnet.ldap_subnet import LDAPSubnet

if TYPE_CHECKING:
    from ..asset_mapper import MappingRegistry


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

        self._CAPABILITIES: "LDAPCapabilities" = LDAPCapabilities(
            ldap_search=self._connector.fetch,
            ldap_obj_opt=self._object_opt,
        )

    # ****************************************************************
    # Methods - LDAP objects

    def ldap_objects(
        self,
        entries: list["LDAPEntry"],
        auto: bool = False,
    ) -> dict[str, "LDAPObject"]:
        """
        Map the provided LDAP entries into a dictionary of LDAPObject instances.

        Args:
            entries (list[LDAPEntry]): LDAP entries to map
            auto (bool)              : Auto map the objects dynamically per type

        Returns:
            dict[str, LDAPComputer]: Mapped entries as a dictionary of LDAP objects
        """

        self.logger.info(f"{Context()}::Mapping {len(entries)} entries into LDAPObjects")

        def map_obj(entry: "LDAPEntry") -> "LDAPObject":
            if auto:
                obj_type = LDAPObjectType.from_object_cls(entry)
                LDAPDynamicObjectType = self._object_opt(obj_type).cls

                return LDAPDynamicObjectType(
                    self._connector.complete_partial_entry(entry), self._CAPABILITIES
                )

            return LDAPObject(entry, capabilities=self._CAPABILITIES)

        objects = {obj.dn: obj for obj in list(map(map_obj, entries))}

        return objects

    def _ldap_computers(self, entries: list["LDAPEntry"]) -> dict[str, "LDAPComputer"]:
        """
        Map the provided LDAP entries into a dictionary of LDAPComputer instances.

        Args:
            entries (list[LDAPEntry]): LDAP entries to map

        Returns:
            dict[str, LDAPComputer]: Mapped entries as a dictionary of LDAP computers
        """

        self.logger.info(f"{Context()}::Mapping {len(entries)} entries into LDAPComputers")

        def map_cpt(entry: "LDAPEntry") -> "LDAPComputer":
            return LDAPComputer(entry, capabilities=self._CAPABILITIES)

        computers = {cpt.dn: cpt for cpt in list(map(map_cpt, entries))}

        return computers

    def _ldap_users(self, entries: list["LDAPEntry"]) -> dict[str, "LDAPUser"]:
        """
        Map the provided LDAP entries into a dictionary of User instances.

        Args:
            entries (list[LDAPEntry]): LDAP entries to map

        Returns:
            dict[str, LDAPUser]: Mapped entries as a dictionary of LDAP computers
        """

        self.logger.info(f"{Context()}::Mapping {len(entries)} entries into LDAPUsers")

        def map_usr(entry: "LDAPEntry") -> "LDAPUser":
            return LDAPUser(entry, capabilities=self._CAPABILITIES)

        users = {usr.dn: usr for usr in list(map(map_usr, entries))}

        return users

    def _ldap_groups(
        self,
        entries: list["LDAPEntry"],
        recursive: bool = False,
    ) -> dict[str, "LDAPGroup"]:
        """
        Map the provided LDAP entries into a dictionary of LDAPGroup instances.

        Args:
            entries (list[LDAPEntry]): LDAP entries to map
            recursive (bool)         : Whether to retrieve group members recursively or not

        Returns:
            dict[str, LDAPGroup]: Mapped entries as a dictionary of LDAP computers
        """

        self.logger.info(f"{Context()}::Mapping {len(entries)} entries into LDAPGroups")

        def map_grp(entry: "LDAPEntry") -> "LDAPGroup":
            grp_instance = LDAPGroup(entry, self._CAPABILITIES)
            if recursive:
                grp_instance.fetch_members(recursive)

            return grp_instance

        groups = {grp.dn: grp for grp in list(map(map_grp, entries))}

        return groups

    def ldap_gpos(self, entries: list["LDAPEntry"]) -> dict[str, "LDAPGroupPolicyObject"]:
        """
        Map the provided LDAP entries into a dictionary of LDAPGroupPolicyObject instances.

        Args:
            entries (list[LDAPEntry]): LDAP entries to map

        Returns:
            dict[str, LDAPGroup]: Mapped entries as a dictionary of LDAP gpos
        """

        def map_gpo(entry: "LDAPEntry") -> "LDAPGroupPolicyObject":
            return LDAPGroupPolicyObject(entry, self._CAPABILITIES)

        gpos = {gpo.dn: gpo for gpo in list(map(map_gpo, entries))}

        return gpos

    def ldap_ous(
        self,
        entries: list["LDAPEntry"],
        recursive: bool = False,
    ) -> dict[str, "LDAPOrganizationalUnit"]:
        """
        Map the provided LDAP entries into a dictionary of LDAPOrganizationalUnit instances.

        Args:
            entries (list[LDAPEntry]): LDAP entries to map
            recursive (bool)         : Retrieve OUs recursively if set to True

        Returns:
            dict[str, LDAPOrganizationalUnit]: Mapped entries as a dictionary of LDAP ous
        """

        self.logger.info(
            f"{Context()}::Mapping {len(entries)} entries into LDAPOrganizationalUnits"
        )

        def map_ou(entry: "LDAPEntry") -> "LDAPOrganizationalUnit":
            ou_instance = LDAPOrganizationalUnit(entry, self._CAPABILITIES)
            if recursive:
                ou_instance.fetch_objects(recursive)

            return ou_instance

        ous = {ou.dn: ou for ou in list(map(map_ou, entries))}

        return ous

    def _ldap_subnets(self, entries: list["LDAPEntry"]) -> dict[str, "LDAPSubnet"]:
        """
        Map the provided LDAP entries into a dictionary of LDAPSubnet instances.

        Args:
            entries (list[LDAPEntry]): LDAP entries to map

        Returns:
            dict[str, LDAPSubnet]: Mapped entries as a dictionary of LDAP ous
        """

        self.logger.info(f"{Context()}::Mapping {len(entries)} entries into LDAPSubnets")

        def map_net(entry: "LDAPEntry") -> "LDAPSubnet":
            return LDAPSubnet(entry, self._CAPABILITIES)

        subnets = {net.dn: net for net in list(map(map_net, entries))}

        return subnets

    def _object_opt(self, ldap_obj_type: "LDAPObjectType") -> "LDAPObjectOptions[LDAPObject]":
        """
        Return an LDAP object based on a given type.

        Args:
            ldap_obj_type (LDAPObjectType): The LDAPObjectType element that will determine the output object

        Returns:
            LDAPObjTypeAlias: The python class matching the provided entry
        """

        obj_map: dict[str, "LDAPObjectOptions"] = {
            f"{LDAPObjectType.DEFAULT}": LDAPObjectOptions["LDAPObject"](
                cls=LDAPObject, fetch=self._connector.objects
            ),
            f"{LDAPObjectType.COMPUTER}": LDAPObjectOptions["LDAPComputer"](
                cls=LDAPComputer, fetch=self._connector.computers
            ),
            f"{LDAPObjectType.GPO}": LDAPObjectOptions["LDAPGroupPolicyObject"](
                cls=LDAPGroupPolicyObject, fetch=self._connector.gpos
            ),
            f"{LDAPObjectType.GROUP}": LDAPObjectOptions["LDAPGroup"](
                cls=LDAPGroup, fetch=self._connector.groups
            ),
            f"{LDAPObjectType.OU}": LDAPObjectOptions["LDAPOrganizationalUnit"](
                cls=LDAPOrganizationalUnit, fetch=self._connector.ous
            ),
            f"{LDAPObjectType.SUBNET}": LDAPObjectOptions["LDAPSubnet"](
                cls=LDAPSubnet, fetch=self._connector.subnets
            ),
            f"{LDAPObjectType.USER}": LDAPObjectOptions["LDAPUser"](
                cls=LDAPUser, fetch=self._connector.users
            ),
        }

        return obj_map[f"{ldap_obj_type}"]

    # ****************************************************************
    # Methods - Asset mapping

    ### Computer mappping
    def computers(self, entries: list["LDAPEntry"]) -> dict[str, "Computer"]:
        """
        Map LDAP entries into Computer instances.

        Args:
            entries (list[LDAPEntry]): Entries to map

        Returns:
            dict[str, Computer]: A dictionary Computer instances
        """

        ldap_cpt = self._ldap_computers(entries)

        self.logger.info(f"{Context()}::Mapping {len(entries)} entries into final Computer asset")

        mapping_registry: "MappingRegistry" = {
            "id": ("computer_id", None),
            "name": ("name", None),
            "description": ("description", None),
            "hostname": ("label", None),
        }

        def mapping_cb(asset: "Computer", record: dict[str, Any]) -> None:
            release_filters: list["OSReleaseListFilter"] = [
                lambda rl: rl.filter_max_version(),
                lambda rl: rl.filter_by_label(record["os"]["name"]),
            ]

            os: "MappingOSTuple" = MappingFunction.OS(
                "os_details_from_str",
                os_str=record["os"]["name"],
                os_ver=record["os"]["version"],
                filters=release_filters,
            )

            os_instance, os_rel, os_edition = os
            if os_instance is not None:
                asset.computer_type = next(iter(os_instance.computer_type))

            asset.os_release = os_rel
            asset.os_edition = os_edition
            asset.add_custom_attr("ldap", record)

        return self.map_many(
            [ cpt.to_dict() for cpt in ldap_cpt.values() ],
            asset_cls=Computer,
            mapping_registry=mapping_registry,
            callback=mapping_cb,
            key_callback=lambda r: r["dn"],
        )
