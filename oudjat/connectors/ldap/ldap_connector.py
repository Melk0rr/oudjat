"""Main module of the LDAP package. Handles connection to an LDAP server and data retrieving operations."""

import socket
import ssl
from typing import TYPE_CHECKING, Dict, List, Union

import ldap3

from oudjat.connectors.connector import Connector
from oudjat.utils.color_print import ColorPrint

from .objects.ldap_entry import LDAPEntry
from .objects.ldap_object import LDAPObject
from .objects.ldap_object_types import LDAPObjectType

if TYPE_CHECKING:
    from .objects.account.group.ldap_group import LDAPGroup
    from .objects.account.ldap_computer import LDAPComputer
    from .objects.account.ldap_user import LDAPUser
    from .objects.gpo.ldap_gpo import LDAPGroupPolicyObject
    from .objects.ou.ldap_ou import LDAPOrganizationalUnit
    from .objects.subnet.ldap_subnet import LDAPSubnet


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

        self.use_tls = use_tls
        self.port = 636 if use_tls else 389

        super().__init__(target=server, service_name=service_name, use_credentials=True)

        self.default_search_base: str = None
        self.ldap_server: ldap3.Server = None
        self.connection: ldap3.Connection = None
        self.domain: str = None

    # ****************************************************************
    # Methods

    def get_domain(self) -> str:
        """
        Return the domain name.

        Returns:
            str: domain name
        """

        return self.domain

    def get_connection(self) -> ldap3.Connection:
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
        self.port = 636 if use_tls else 389

    def connect(self, version: ssl._SSLMethod = None) -> None:
        """
        Initiate connection to target server.

        Args:
            version (ssl._SSLMethod): SSL/TLS version
        """

        if version is None:
            try:
                self.connect(version=ssl.PROTOCOL_TLSv1_2)

            except ldap3.core.exceptions.LDAPSocketOpenError as e:
                if not self.use_tls:
                    ColorPrint.yellow(
                        f"{__class__.__name__}.connect::Error while trying to connect to LDAP: {e}"
                    )

                self.connect(version=ssl.PROTOCOL_TLSv1)

            return

        target_ip = socket.gethostbyname(self.target)

        if not target_ip:
            raise Exception(
                f"{__class__.__name__}.connect::The target {self.target} is unreachable"
            )

        tls_option = {"use_ssl": self.use_tls}
        if self.use_tls:
            tls_option["tls"] = ldap3.Tls(
                validate=ssl.CERT_NONE, version=version, ciphers="ALL:@SECLEVEL=0"
            )

        ldap_server = ldap3.Server(target_ip, get_info=ldap3.ALL, port=self.port, **tls_option)

        ldap_connection = ldap3.Connection(
            ldap_server,
            user=self.credentials.username,
            password=self.credentials.password,
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

    def search(
        self,
        search_type: "LDAPObjectType" = LDAPObjectType.DEFAULT,
        search_base: str = None,
        search_filter: str = None,
        attributes: Union[str, List[str]] = None,
        **kwargs,
    ) -> List[LDAPEntry]:
        """
        Run an LDAP search based on the provided parameters.

        Args:
            search_type (str)           : search type (see ldap_object_type.py for details)
            search_base (str)           : search base (location in domain tree)
            search_filter (str)         : search filter
            attributes (str | List[str]): attributes to include in the result
            **kwargs (Dict)             : any other argument to pass

        Returns:
            List[LDAPEntry]: list of ldap entries
        """

        if self.connection is None:
            raise ConnectionError(
                f"{__class__.__name__}.search::You must initiate connection to {self.target} before running search !"
            )

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

        return list(
            map(
                LDAPConnector.ldap_entry_from_dict,
                filter(LDAPConnector.check_entry_type, results),
            )
        )

    def get_mapped_object(
        self,
        search_type: "LDAPObjectType",
        search_base: str = None,
        search_filter: str = None,
        attributes: Union[str, List[str]] = None,
    ) -> List["LDAPObject"]:
        """
        Generitc method to generate LDAPObject instances based on an LDAP entry search result.

        Args:
            search_type (LDAPObjectType): ldap object type used to map the results
            search_base (str)           : where to base the search on in terms of directory location
            search_filter (str)         : filter to reduce search results
            attributes (str | List[str]): attributes to include in result

        Returns:
            List[LDAPComputer]: list of computers
        """

        entries = self.search(
            search_type=search_type,
            search_base=search_base,
            search_filter=search_filter,
            attributes=attributes,
        )

        return self.map_entries(entries, ldap_cls=search_type.python_cls)

    def get_gpo(
        self, displayName: str = "*", name: str = "*", attributes: Union[str, List[str]] = None
    ) -> List["LDAPGroupPolicyObject"]:
        """
        Specific method to retrieve LDAP GPO instances.

        Args:
            displayName (str)           : GPO display name
            name (str)                  : GPO name
            attributes (str | List[str]): attributes to include in result

        Returns:
            List[LDAPGroupPolicyObject]: list of LDAPGroupPolicyObject instances
        """

        return self.get_mapped_object(
            search_type=LDAPObjectType.GPO,
            search_base=None,
            search_filter=f"(displayName={displayName})(name={name})",
            attributes=attributes,
        )

    def get_subnet(
        self, search_filter: str = None, attributes: Union[str, List[str]] = None
    ) -> List["LDAPSubnet"]:
        """
        Specific method to retrieve LDAP subnet instances.

        Args:
            search_filter (str)         : filter to reduce search results
            attributes (str | List[str]): attributes to include in result

        Returns:
            List[LDAPSubnet]: list of subnets
        """

        sb_dc = ",".join([f"DC={dc.lower()}" for dc in self.domain.split(".")])

        return self.get_mapped_object(
            search_type=LDAPObjectType.SUBNET,
            search_base=f"CN=Subnets,CN=Sites,CN=Configuration,{sb_dc}",
            search_filter=search_filter,
            attributes=attributes,
        )

    def get_computer(
        self,
        search_filter: str = None,
        attributes: Union[str, List[str]] = None,
        search_base: str = None,
    ) -> List["LDAPComputer"]:
        """
        Specific method to retrieve LDAP Computer instances.

        Args:
            search_filter (str)         : filter to reduce search results
            attributes (str | List[str]): attributes to include in result
            search_base (str)           : where to base the search on in terms of directory location

        Returns:
            List[LDAPComputer]: list of computers
        """

        return self.get_mapped_object(
            search_type=LDAPObjectType.COMPUTER,
            search_base=search_base,
            search_filter=search_filter,
            attributes=attributes,
        )

    def get_users(
        self,
        search_filter: str = None,
        attributes: Union[str, List[str]] = None,
        search_base: str = None,
    ) -> List["LDAPUser"]:
        """
        Specific method to retrieve LDAP User instances.

        Args:
            search_filter (str)         : filter to reduce search results
            attributes (str | List[str]): attributes to include in result
            search_base (str)           : where to base the search on in terms of directory location

        Returns:
            List[LDAPUser]: list of users
        """

        return self.get_mapped_object(
            search_type=LDAPObjectType.USER,
            search_base=search_base,
            search_filter=search_filter,
            attributes=attributes,
        )

    def get_group_members(
        self, ldap_group: "LDAPGroup", recursive: bool = False
    ) -> List["LDAPObject"]:
        """
        Retrieve and returns the members of the given group.

        Args:
            ldap_group (LDAPGroup): group to retrieve members from
            recursive (bool)      : wheither to retrieve members recursively or not

        Returns:
            List[LDAPObject]: list of members
        """

        members = []
        for ref in ldap_group.get_member_refs():
            # INFO: Search for the ref in LDAP server
            # TODO: Must implement an LDAPFilter class to handle potential escape characters
            escaped_ref = ldap3.utils.conv.escape_filter_chars(ref)
            ref_search = self.search(search_filter=f"(distinguishedName={escaped_ref})")

            if len(ref_search) > 0:
                ref_search: LDAPEntry = ref_search[0]
                obj_type = ref_search.get_type()

                new_member: "LDAPObject" = LDAPObjectType.get_ldap_class(obj_type)(
                    ldap_entry=ref_search
                )

                if new_member.get_type() == "GROUP" and recursive:
                    new_member.get_members(ldap_connector=self, recursive=recursive)

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

        member_ref_list = ldap_group.get_members_flat(ldap_connector=self) if extended else ldap_group.members.values()
        return ldap_object.get_uuid() in [m.get_id() for m in member_ref_list]

    def get_ou(
        self,
        dn: str = None,
        search_filter: str = None,
        search_base: str = None,
        attributes: Union[str, List[str]] = None,
    ) -> List["LDAPOrganizationalUnit"]:
        """
        Specific method to retrieve LDAP organizational unit objects.

        Args:
            dn (str):                   : optional distinguished name to search
            search_filter (str)         : filter to reduce search results
            attributes (str | List[str]): attrbutes to include in result
            search_base (str)           : where to base the search on in terms of directory location

        Returns:
            List[LDAPOrganizationalUnit]: list of OU matching filter
        """

        return self.get_mapped_object(
            search_type=LDAPObjectType.OU,
            search_base=search_base,
            search_filter=search_filter,
            attributes=attributes,
        )

    def get_ou_objects(
        self,
        ldap_ou: "LDAPOrganizationalUnit",
        object_types: List[str] = None,
        recursive: bool = False,
    ) -> List["LDAPEntry"]:
        """
        Retrieve the members of a given organizational unit (OU).

        This method fetches all LDAP entries that are direct children or descendants of the specified organizational unit.
        It supports filtering by object types and can recursively search through all sub-OUs if requested.

        Args:
            ldap_ou (LDAPOrganizationalUnit)  : An object representing the organizational unit from which to retrieve members. It must have a method to get its distinguished name (`get_dn`).
            object_types (List[str], optional): A list of strings representing the types of objects to filter by. If provided, only entries with these object classes will be returned. Defaults to None.
            recursive (bool, optional)        : A boolean indicating whether to search recursively through all sub-OUs. If True, it will include descendants in the search results. Defaults to False.

        Returns:
            List[LDAPEntry]: A list of LDAP entries that are either direct children or descendants of the specified organizational unit. Each entry is represented by an `LDAPEntry` object.
        """

        search_args = {"search_base": ldap_ou.get_dn()}

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
            search_type=LDAPObjectType.from_object_cls(ldap_entry.get_type()),
            search_filter=f"(distinguishedName={ldap_entry.get_dn()})",
        )

    def get_domain_admins(self) -> List[LDAPEntry]:
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
    def map_entries(entries: List["LDAPEntry"], ldap_cls: "LDAPObject") -> List["LDAPObject"]:
        """
        Map a list of ldap entries to a list of the provided LDAP class.

        Args:
            entries (List[LDAPEntry]): list of entries to map
            ldap_cls (LDAPObject)    : ldap class used to map

        Returns:
            List[LDAPObject]: mapped list of ldap object
        """

        if not issubclass(ldap_cls, LDAPObject):
            raise ValueError(
                f"{__class__.__name__}.map_entries::Invalid class provided. Please provide a valid LDAPObject instance"
            )

        return list(map(ldap_cls, entries))

    @staticmethod
    def check_entry_type(entry: Dict) -> bool:
        """
        Check if the provided entry is a searchResEntry.

        Args:
            entry (Dict): entry to check

        Returns:
            bool: True if the entry is a searchResEntry. False otherwise
        """

        return entry["type"] == "searchResEntry"

    @staticmethod
    def ldap_entry_from_dict(entry: Dict) -> "LDAPEntry":
        """
        Create an LDAPEntry from the provided dictionary.

        Args:
            entry (Dict): entry to convert into an LDAPEntry

        Returns:
            LDAPEntry: the new LDAPEntry instance
        """

        if entry.get("attributes", None) is None:
            raise ValueError(f"{__class__.__name__}.ldap_entry_from_dict::Invalid entry provided")

        return LDAPEntry(**entry)
