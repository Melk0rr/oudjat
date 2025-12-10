"""
A module that handle LDAP entry mapping to asset elements.
"""

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


class LDAPAssetMapper:
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

        self._connector: "LDAPConnector" = ldapco

        self._MAP: dict[str, "LDAPObjectOptions"] = {
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

        self._CAPABILITIES: "LDAPCapabilities" = LDAPCapabilities(
            ldap_search=self._connector.fetch,
            ldap_obj_opt=self._object_opt,
        )

    # ****************************************************************
    # Methods

    def objects(
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

        def map_obj(entry: "LDAPEntry") -> "LDAPObject":
            if auto:
                obj_type = LDAPObjectType.from_object_cls(entry)
                LDAPDynamicObjectType = self._MAP[obj_type.name].cls

                return LDAPDynamicObjectType(
                    self._connector.complete_partial_entry(entry), self._CAPABILITIES
                )

            return LDAPObject(entry, capabilities=self._CAPABILITIES)

        objects = {obj.dn: obj for obj in list(map(map_obj, entries))}

        return objects

    def computers(self, entries: list["LDAPEntry"]) -> dict[str, "LDAPComputer"]:
        """
        Map the provided LDAP entries into a dictionary of LDAPComputer instances.

        Args:
            entries (list[LDAPEntry]): LDAP entries to map

        Returns:
            dict[str, LDAPComputer]: Mapped entries as a dictionary of LDAP computers
        """

        def map_cpt(entry: "LDAPEntry") -> "LDAPComputer":
            return LDAPComputer(entry, capabilities=self._CAPABILITIES)

        computers = {cpt.dn: cpt for cpt in list(map(map_cpt, entries))}

        return computers

    def users(self, entries: list["LDAPEntry"]) -> dict[str, "LDAPUser"]:
        """
        Map the provided LDAP entries into a dictionary of User instances.

        Args:
            entries (list[LDAPEntry]): LDAP entries to map

        Returns:
            dict[str, LDAPComputer]: Mapped entries as a dictionary of LDAP computers
        """

        def map_usr(entry: "LDAPEntry") -> "LDAPUser":
            return LDAPUser(entry, capabilities=self._CAPABILITIES)

        users = {usr.dn: usr for usr in list(map(map_usr, entries))}

        return users

    def groups(
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

        def map_grp(entry: "LDAPEntry") -> "LDAPGroup":
            grp_instance = LDAPGroup(entry, self._CAPABILITIES)
            if recursive:
                grp_instance.fetch_members(recursive)

            return grp_instance

        groups = {grp.dn: grp for grp in list(map(map_grp, entries))}

        return groups

    def gpos(self, entries: list["LDAPEntry"]) -> dict[str, "LDAPGroupPolicyObject"]:
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

    def ous(
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

        def map_ou(entry: "LDAPEntry") -> "LDAPOrganizationalUnit":
            ou_instance = LDAPOrganizationalUnit(entry, self._CAPABILITIES)
            if recursive:
                ou_instance.fetch_objects(recursive)

            return ou_instance

        ous = {ou.dn: ou for ou in list(map(map_ou, entries))}

        return ous

    def subnets(self, entries: list["LDAPEntry"]) -> dict[str, "LDAPSubnet"]:
        """
        Map the provided LDAP entries into a dictionary of LDAPSubnet instances.

        Args:
            entries (list[LDAPEntry]): LDAP entries to map

        Returns:
            dict[str, LDAPSubnet]: Mapped entries as a dictionary of LDAP ous
        """

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

        return self._MAP[f"{ldap_obj_type}"]
