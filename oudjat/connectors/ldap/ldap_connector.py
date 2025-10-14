"""Main module of the LDAP package. Handles connection to an LDAP server and data retrieving operations."""

import socket
import ssl
from enum import IntEnum
from typing import TYPE_CHECKING, Any, TypedDict, override

import ldap3
from ldap3.core.exceptions import LDAPSocketOpenError
from ldap3.utils.conv import escape_filter_chars

from oudjat.connectors.connector import Connector
from oudjat.utils.color_print import ColorPrint
from oudjat.utils.types import StrType

from .objects.ldap_entry import LDAPEntry
from .objects.ldap_object_types import LDAPObjectType

if TYPE_CHECKING:
    from .objects.account.group.ldap_group import LDAPGroup
    from .objects.account.ldap_computer import LDAPComputer
    from .objects.account.ldap_user import LDAPUser
    from .objects.gpo.ldap_gpo import LDAPGroupPolicyObject
    from .objects.ldap_object import LDAPObject
    from .objects.ldap_object_utilities import LDAPObjectBoundType
    from .objects.ou.ldap_ou import LDAPOrganizationalUnit
    from .objects.subnet.ldap_subnet import LDAPSubnet

LDAPObjListTypeAlias = list[LDAPObject | LDAPComputer | LDAPGroup | LDAPUser | LDAPOrganizationalUnit | LDAPGroupPolicyObject]

class LDAPPort(IntEnum):
    """
    A simple enumeration of possible LDAP ports.

    Attributes:
        DEFAULT: default ldap port
        TLS    : LDAP over TLS port
    """

    DEFAULT = 389
    TLS = 636


class LDAPConnector(Connector):
    """
    LDAP connector to interact and query LDAP servers.

    Provides a centralized way to connect to an LDAP server and run queries to retrieve informations on different kind of objects
    - Users
    - Computers
    - Organizational Units
    - Group Policy Objects
    - More...
    """

    # ****************************************************************
    # Attributes & Constructors

    LDAP_PYTHON_CLS: dict[str, LDAPObjectBoundType] = {
        f"{LDAPObjectType.DEFAULT}": LDAPObject,
        f"{LDAPObjectType.COMPUTER}": LDAPComputer,
        f"{LDAPObjectType.GPO}": LDAPGroupPolicyObject,
        f"{LDAPObjectType.GROUP}": LDAPGroup,
        f"{LDAPObjectType.OU}": LDAPOrganizationalUnit,
        f"{LDAPObjectType.SUBNET}": LDAPSubnet,
        f"{LDAPObjectType.USER}": LDAPUser,
    }

    def __init__(
        self, server: str, service_name: str = "OudjatLDAPConnection", use_tls: bool = False
    ) -> None:
        """
        Create a new LDAPConnector.

        Args:
            server (str)      : server name
            service_name (str): service name used to store credentials
            use_tls (bool)    : should the connector use TLS for LDAPS connection
        """

        self.use_tls: bool = use_tls
        self.port: LDAPPort = LDAPPort.TLS if use_tls else LDAPPort.DEFAULT

        super().__init__(target=server, service_name=service_name, use_credentials=True)

        self.domain: str = ""
        self.default_search_base: str = ""
        self.ldap_server: ldap3.Server
        self.connection: ldap3.Connection | None = None

    # ****************************************************************
    # Methods

    def get_domain(self) -> str:
        """
        Return the domain name.

        Returns:
            str: domain name
        """

        return self.domain

    def get_connection(self) -> ldap3.Connection | None:
        """
        Return the server connection.

        Returns:
            ldap3.Connection: active connection
        """

        return self.connection

    def get_default_search_base(self) -> str:
        """
        Return the default search base.

        Returns:
            str: default domain search base
        """

        return self.default_search_base

    def set_tls_usage(self, use_tls: bool = True) -> None:
        """
        Set the TLS usage.

        Args:
            use_tls (bool): should the connector use TLS
        """

        self.use_tls = use_tls
        self.port = LDAPPort.TLS if use_tls else LDAPPort.DEFAULT

    # TODO: Make a type alias for tls versions
    @override
    def connect(self, version: "ssl._SSLMethod | None" = None) -> None:
        """
        Initiate connection to target server.

        Args:
            version (ssl._SSLMethod): SSL/TLS version
        """

        if version is None:
            try:
                self.connect(version=ssl.PROTOCOL_TLSv1_2)

            except LDAPSocketOpenError as e:
                if not self.use_tls:
                    ColorPrint.yellow(
                        f"{__class__.__name__}.connect::Error while trying to connect to LDAP: {e}"
                    )

                self.connect(version=ssl.PROTOCOL_TLSv1)

            return

        target_ip = socket.gethostbyname(str(self.target))

        if not target_ip:
            raise Exception(
                f"{__class__.__name__}.connect::The target {self.target} is unreachable"
            )

        TLSOption = TypedDict("TLSOption", {"use_ssl": bool, "tls": ldap3.Tls | None})
        tls_option: TLSOption = {"use_ssl": self.use_tls, "tls": None}

        if self.use_tls:
            tls_option["tls"] = ldap3.Tls(
                validate=ssl.CERT_NONE, version=version, ciphers="ALL:@SECLEVEL=0"
            )

        ldap_server = ldap3.Server(target_ip, get_info=ldap3.ALL, port=self.port, **tls_option)

        if self._credentials is None:
            raise ConnectionError(
                f"{__class__.__name__}.connect::No credentials have been defined to connect to {self.target}"
            )

        ldap_connection = ldap3.Connection(
            ldap_server,
            user=self._credentials.username,
            password=self._credentials.password,
            auto_referrals=False,
            authentication=ldap3.NTLM,
        )

        if not ldap_connection.bound:
            bind_result = ldap_connection.bind()

            if not bind_result:
                result = ldap_connection.result

                if result["result"] == "RESULT_STRONGER_AUTH_REQUIRED" and self.use_tls:
                    self.set_tls_usage(use_tls=True)
                    return self.connect()

                if (
                    result["description"] == "invalidCredentials"
                    and result["message"].split(":")[0] == "80090346"
                ):
                    raise Exception(
                        f"{__class__.__name__}.connect::LDAP channel binding required. Use -scheme ldaps -ldap-channel-binding"
                    )

                raise Exception(
                    f"{__class__.__name__}.connect::Failed LDAP authentication ({result['description']}) {result['message']}]"
                )

        if ldap_server.schema is None:
            ldap_server.get_info_from_server(ldap_connection)

            if ldap_connection.result["result"] != 0:
                if ldap_connection.result["message"].split(":")[0] == "000004DC":
                    raise Exception(
                        f"{__class__.__name__}.connect::Failed to bind to LDAP. Most likely due to an invalid username"
                    )

            if ldap_server.schema is None:
                raise Exception(f"{__class__.__name__}.connect::Failed to get LDAP schema")

        ColorPrint.green(f"Bound to {ldap_server}")

        self.ldap_server = ldap_server
        self.connection = ldap_connection

        self.default_search_base = self.ldap_server.info.other["defaultNamingContext"][0]
        self.domain = self.ldap_server.info.other["ldapServiceName"][0].split("@")[-1]

    @override
    def search(
        self,
        search_type: "LDAPObjectType | str" = LDAPObjectType.DEFAULT,
        search_base: str | None = None,
        search_filter: str | None = None,
        attributes: StrType | None = None,
        **kwargs: Any,
    ) -> list[LDAPEntry]:
        """
        Run an LDAP search based on the provided parameters.

        Args:
            search_type (str)           : search type (see ldap_object_type.py for details)
            search_base (str)           : search base (location in domain tree)
            search_filter (str)         : search filter
            attributes (str | list[str]): attributes to include in the result
            **kwargs (Dict)             : any other argument to pass

        Returns:
            list[LDAPEntry]: list of ldap entries
        """

        if self.connection is None:
            raise ConnectionError(
                f"{__class__.__name__}.search::You must initiate connection to {self.target} before running search !"
            )

        if isinstance(search_type, str):
            search_type = LDAPObjectType[search_type]

        # INFO: If the search type is default : final filter is equal to provided search filter
        # Else final filter is a combination of filter matching search type + provided search filter
        formated_filter = search_type.filter
        if search_type == LDAPObjectType.DEFAULT and search_filter is not None:
            formated_filter = search_filter

        elif search_filter is not None:
            formated_filter = f"(&{formated_filter}{search_filter})"

        results = self.connection.extend.standard.paged_search(
            search_base=search_base or self.default_search_base,
            search_filter=formated_filter,
            attributes=attributes or search_type.attributes,
            generator=False,
            **kwargs,
        )

        def ldap_entry_from_dict(entry: dict[str, Any]) -> "LDAPEntry":

            if entry.get("attributes", None) is None:
                raise ValueError(f"{__class__.__name__}.ldap_entry_from_dict::Invalid entry provided")

            entry["ldap_obj_type"] = LDAPObjectType.from_object_cls(LDAPObjectType.resolve_entry_type(entry))
            entry["ldap_search"] = self.search
            entry["ldap_python_cls"] = LDAPConnector.ldap_python_cls_from_obj_type

            return LDAPEntry(**entry)

        return list(
            map(
                ldap_entry_from_dict,
                filter(LDAPConnector.check_entry_type, results),
            )
        )

    def get_gpo(
        self, displayName: str = "*", name: str = "*", attributes: StrType | None = None
    ) -> list["LDAPGroupPolicyObject"]:
        """
        Specific method to retrieve LDAP GPO instances.

        Args:
            displayName (str)           : GPO display name
            name (str)                  : GPO name
            attributes (str | list[str]): attributes to include in result

        Returns:
            list[LDAPGroupPolicyObject]: list of LDAPGroupPolicyObject instances
        """

        entries = self.search(
            search_type=LDAPObjectType.GPO,
            search_base=None,
            search_filter=f"(displayName={displayName})(name={name})",
            attributes=attributes,
        )

        return LDAPConnector.map_entries(entries, LDAPObjectType.GPO.value.python_cls)

    def get_subnet(
        self, search_filter: str | None = None, attributes: StrType | None = None
    ) -> list["LDAPSubnet"]:
        """
        Specific method to retrieve LDAP subnet instances.

        Args:
            search_filter (str)         : filter to reduce search results
            attributes (str | list[str]): attributes to include in result

        Returns:
            list[LDAPSubnet]: list of subnets
        """

        sb_dc = ",".join([f"DC={dc.lower()}" for dc in self.domain.split(".")])

        entries = self.search(
            search_type=LDAPObjectType.SUBNET,
            search_base=f"CN=Subnets,CN=Sites,CN=Configuration,{sb_dc}",
            search_filter=search_filter,
            attributes=attributes,
        )

        return LDAPConnector.map_entries(entries, LDAPSubnet)

    def get_computer(
        self,
        search_filter: str | None = None,
        attributes: StrType | None = None,
        search_base: str | None = None,
    ) -> list["LDAPComputer"]:
        """
        Specific method to retrieve LDAP Computer instances.

        Args:
            search_filter (str)         : filter to reduce search results
            attributes (str | list[str]): attributes to include in result
            search_base (str)           : where to base the search on in terms of directory location

        Returns:
            list[LDAPComputer]: list of computers
        """

        entries = self.search(
            search_type=LDAPObjectType.COMPUTER,
            search_base=search_base,
            search_filter=search_filter,
            attributes=attributes,
        )

        return LDAPConnector.map_entries(entries, LDAPComputer)

    def get_users(
        self,
        search_filter: str | None = None,
        attributes: StrType | None = None,
        search_base: str | None = None,
    ) -> list["LDAPUser"]:
        """
        Specific method to retrieve LDAP User instances.

        Args:
            search_filter (str)         : filter to reduce search results
            attributes (str | List[str]): attributes to include in result
            search_base (str)           : where to base the search on in terms of directory location

        Returns:
            list[LDAPUserTypeAlias]: list of users
        """

        entries = self.search(
            search_type=LDAPObjectType.USER,
            search_base=search_base,
            search_filter=search_filter,
            attributes=attributes,
        )

        return LDAPConnector.map_entries(entries, LDAPUser)

    def get_group_members(
        self, ldap_group: "LDAPGroup", recursive: bool = False
    ) -> list["LDAPObject"]:
        """
        Retrieve and returns the members of the given group.

        Args:
            ldap_group (LDAPGroup): group to retrieve members from
            recursive (bool)      : wheither to retrieve members recursively or not

        Returns:
            list[LDAPObject]: list of members
        """

        members = []
        for ref in ldap_group.get_member_refs():
            # INFO: Search for the ref in LDAP server
            # TODO: Must implement an LDAPFilter class to handle potential escape characters
            escaped_ref = escape_filter_chars(ref)
            ref_search: list[LDAPEntry] = self.search(
                search_filter=f"(distinguishedName={escaped_ref})"
            )

            if len(ref_search) > 0:
                search_entry: LDAPEntry = ref_search[0]
                obj_type = LDAPObjectType.resolve_entry_type(search_entry)

                new_member = LDAPObjectType.get_python_class(obj_type)(ldap_entry=search_entry)
                if isinstance(new_member, LDAPGroup) and recursive:
                    new_member.fetch_members(ldap_connector=self, recursive=recursive)

                members.append(new_member)

        return members

    def is_object_member_of(
        self, ldap_object: "LDAPObject", ldap_group: "LDAPGroup", extended: bool = False
    ) -> bool:
        """
        Check wheither the given object is member of the giver group.

        Args:
            ldap_object (LDAPObject): object to check membership of
            ldap_group (LDAPGroup)  : group to check object membership
            extended (bool)         : wheither to extend the search to sub group or not

        Returns:
            bool: wheither the object is a member of the group or not
        """

        member_ref_list = (
            ldap_group.get_members_flat(ldap_connector=self)
            if extended
            else ldap_group.members.values()
        )
        return ldap_object.id in [m.id for m in member_ref_list]

    def get_ou(
        self,
        search_filter: str | None = None,
        search_base: str | None = None,
        attributes: StrType | None = None,
    ) -> list["LDAPOrganizationalUnit"]:
        """
        Specific method to retrieve LDAP organizational unit objects.

        Args:
            dn (str):                   : optional distinguished name to search
            search_filter (str)         : filter to reduce search results
            attributes (str | List[str]): attrbutes to include in result
            search_base (str)           : where to base the search on in terms of directory location

        Returns:
            list[LDAPOrganizationalUnit]: list of OU matching filter
        """

        entries = self.search(
            search_type=LDAPObjectType.OU,
            search_base=search_base,
            search_filter=search_filter,
            attributes=attributes,
        )

        return LDAPConnector.map_entries(entries, LDAPObjectType.OU.value.python_cls)

    def get_ou_objects(
        self,
        ldap_ou: "LDAPOrganizationalUnit",
        object_types: list[str] | None = None,
        recursive: bool = False,
    ) -> list["LDAPEntry"]:
        """
        Retrieve the members of a given organizational unit (OU).

        This method fetches all LDAP entries that are direct children or descendants of the specified organizational unit.
        It supports filtering by object types and can recursively search through all sub-OUs if requested.

        Args:
            ldap_ou (LDAPOrganizationalUnit)  : An object representing the organizational unit from which to retrieve members. It must have a method to get its distinguished name (`get_dn`).
            object_types (List[str], optional): A list of strings representing the types of objects to filter by. If provided, only entries with these object classes will be returned. Defaults to None.
            recursive (bool, optional)        : A boolean indicating whether to search recursively through all sub-OUs. If True, it will include descendants in the search results. Defaults to False.

        Returns:
            list[LDAPEntry]: A list of LDAP entries that are either direct children or descendants of the specified organizational unit. Each entry is represented by an `LDAPEntry` object.
        """

        search_args: dict[str, Any] = {"search_base": ldap_ou.get_dn()}

        if object_types is not None:
            types_filter_str = "".join([f"(objectClass={t})" for t in object_types])
            search_args["search_filter"] = f"(|{types_filter_str})"

        # TODO: handle recursieve arguments
        return self.search(attributes="*", **search_args)

    def complete_partial_entry(self, ldap_entry: "LDAPEntry") -> "LDAPEntry":
        """
        Completes a partial LDAP entry by searching for the full details of the entry in the LDAP directory.

        This method takes an `LDAPEntry` object and performs a search operation to fetch the complete details of the entry.
        The search is conducted using the distinguished name (DN) of the provided `LDAPEntry`.

        Args:
            self (object): The instance of the class containing this method, typically a class that interacts with an LDAP directory.
            ldap_entry (LDAPEntry): An object representing a partial entry in the LDAP directory. It must have methods to get its type and distinguished name (`get_type` and `get_dn` respectively).

        Returns:
            LDAPEntry: A complete LDAP entry that matches the provided partial entry, including all details found in the search operation.
        """

        return self.search(
            search_type=LDAPObjectType.from_object_cls(LDAPObjectType.resolve_entry_type(ldap_entry)),
            search_filter=f"(distinguishedName={ldap_entry.dn})",
        )[0]

    def get_domain_admins(self) -> list["LDAPEntry"]:
        """
        Return a list of the domain and enterprise admins.

        Returns:
            List[LDAPEntry]: a list of LDAPEntry instances representing the domain admins
        """

        return self.search(
            search_type=LDAPObjectType.USER,
            search_filter="(&(objectClass=user)(objectCategory=Person)(adminCount=1))",
        )

    # ****************************************************************
    # Static methods

    @staticmethod
    def map_entries_from_str(entries: list["LDAPEntry"], ldap_obj_type: str) -> "LDAPObjListTypeAlias":
        """
        Map a list of ldap entries to a list of an LDAPObject type matching the provided string.

        Args:
            entries (list[LDAPEntry]): List of entries to map
            ldap_obj_type (str)      : LDAPObjectType name the python class will be used to map the provided entries

        Returns:
            LDAPObjListTypeAlias: mapped list of ldap object
        """

        return LDAPConnector.map_entries(entries, ldap_cls=LDAPObjectType[ldap_obj_type].value.python_cls)

    @staticmethod
    def map_entries(
        entries: list["LDAPEntry"], ldap_cls: type["LDAPObjectBoundType"]
    ) -> list[LDAPObjectBoundType]:
        """
        Map a list of ldap entries to a list of the provided LDAP class.

        Args:
            entries (list[LDAPEntry]): List of entries to map
            ldap_cls (LDAPObject)    : LDAP class used to map

        Returns:
            list[LDAPObject]: mapped list of ldap object
        """

        return list(map(ldap_cls, entries))

    @staticmethod
    def check_entry_type(entry: dict[str, Any]) -> bool:
        """
        Check if the provided entry is a searchResEntry.

        Args:
            entry (dict[str, Any]): entry to check

        Returns:
            bool: True if the entry is a searchResEntry. False otherwise
        """

        return entry["type"] == "searchResEntry"

    @staticmethod
    def ldap_entry_from_dict(entry: dict[str, Any]) -> "LDAPEntry":
        """
        Create an LDAPEntry from the provided dictionary.

        Args:
            entry (dict[str, Any]): entry to convert into an LDAPEntry

        Returns:
            LDAPEntry: the new LDAPEntry instance
        """

        if entry.get("attributes", None) is None:
            raise ValueError(f"{__class__.__name__}.ldap_entry_from_dict::Invalid entry provided")

        return LDAPEntry(**entry)

    @staticmethod
    def ldap_python_cls_from_obj_type(ldap_obj_type_name: str) -> "LDAPObjectBoundType":
        """
        Return an LDAPObjectBoundType based on a given LDAPEntry.

        Args:
            ldap_obj_type_name (str): The LDAPObjectType element name

        Returns:
            LDAPObjectBoundType: the python class matching the provided entry
        """

        return LDAPConnector.LDAP_PYTHON_CLS[ldap_obj_type_name]

