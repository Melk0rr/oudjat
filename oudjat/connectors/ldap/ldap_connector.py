"""Main module of the LDAP package. Handles connection to an LDAP server and data retrieving operations."""

import socket
import ssl
from enum import IntEnum
from typing import TYPE_CHECKING, Any, TypedDict, final, override

import ldap3
from ldap3.core.exceptions import LDAPSocketOpenError

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
    from .objects.ldap_object import LDAPCapabilities, LDAPObject, LDAPObjectOptions
    from .objects.ou.ldap_ou import LDAPOrganizationalUnit
    from .objects.subnet.ldap_subnet import LDAPSubnet


class LDAPTLSVersion(IntEnum):
    """
    A helper enumeration to describe TLS versions.
    """

    TLSv1 = ssl.PROTOCOL_TLSv1
    TLSv1_1 = ssl.PROTOCOL_TLSv1_1
    TLSv1_2 = ssl.PROTOCOL_TLSv1_2


class LDAPPort(IntEnum):
    """
    A simple enumeration of possible LDAP ports.

    Attributes:
        DEFAULT: default ldap port
        TLS    : LDAP over TLS port
    """

    DEFAULT = 389
    TLS = 636


@final
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

        self._use_tls: bool = use_tls
        self._port: LDAPPort = LDAPPort.TLS if use_tls else LDAPPort.DEFAULT

        super().__init__(target=server, service_name=service_name, use_credentials=True)

        self._domain: str = ""
        self._default_search_base: str = ""
        self._ldap_server: ldap3.Server
        self._connection: ldap3.Connection | None = None

        self._LDAP_PYTHON_CLS: dict[str, "LDAPObjectOptions"] = {
            f"{LDAPObjectType.DEFAULT}": LDAPObjectOptions["LDAPObject"](
                cls=LDAPObject, fetch=self.get_object
            ),
            f"{LDAPObjectType.COMPUTER}": LDAPObjectOptions["LDAPComputer"](
                cls=LDAPComputer, fetch=self.get_computer
            ),
            f"{LDAPObjectType.GPO}": LDAPObjectOptions["LDAPGroupPolicyObject"](
                cls=LDAPGroupPolicyObject, fetch=self.get_gpo
            ),
            f"{LDAPObjectType.GROUP}": LDAPObjectOptions["LDAPGroup"](
                cls=LDAPGroup, fetch=self.get_group
            ),
            f"{LDAPObjectType.OU}": LDAPObjectOptions["LDAPOrganizationalUnit"](
                cls=LDAPOrganizationalUnit, fetch=self.get_ou
            ),
            f"{LDAPObjectType.SUBNET}": LDAPObjectOptions["LDAPSubnet"](
                cls=LDAPSubnet, fetch=self.get_subnet
            ),
            f"{LDAPObjectType.USER}": LDAPObjectOptions["LDAPUser"](
                cls=LDAPUser, fetch=self.get_user
            ),
        }

        self._DEFAULT_CAPABILITIES: LDAPCapabilities = LDAPCapabilities(
            ldap_search=self.search,
            ldap_obj_opt=self.ldap_object_opt_from_obj_type,
        )

    # ****************************************************************
    # Methods

    @property
    def domain(self) -> str:
        """
        Return the domain name.

        Returns:
            str: domain name
        """

        return self._domain

    @property
    @override
    def connection(self) -> ldap3.Connection | None:
        """
        Return the server connection.

        Returns:
            ldap3.Connection: active connection
        """

        return self._connection

    @property
    def default_search_base(self) -> str:
        """
        Return the default search base.

        Returns:
            str: default domain search base
        """

        return self._default_search_base

    def set_tls_usage(self, use_tls: bool = True) -> None:
        """
        Set the TLS usage.

        Args:
        use_tls (bool): should the connector use TLS
        """

        self._use_tls = use_tls
        self._port = LDAPPort.TLS if use_tls else LDAPPort.DEFAULT

    @override
    def connect(self, version: "LDAPTLSVersion | None" = None) -> None:
        """
        Initiate connection to target server.

        Args:
            version (ssl._SSLMethod): SSL/TLS version
        """

        if version is None:
            try:
                self.connect(version=LDAPTLSVersion.TLSv1_2)

            except LDAPSocketOpenError as e:
                if not self._use_tls:
                    ColorPrint.yellow(
                        f"{__class__.__name__}.connect::Error while trying to connect to LDAP: {e}"
                    )

                self.connect(version=LDAPTLSVersion.TLSv1)

            return

        target_ip = socket.gethostbyname(str(self.target))
        if not target_ip:
            raise Exception(
                f"{__class__.__name__}.connect::The target {self.target} is unreachable"
            )

        TLSOption = TypedDict("TLSOption", {"use_ssl": bool, "tls": ldap3.Tls | None})
        tls_option: TLSOption = {"use_ssl": self._use_tls, "tls": None}

        if self._use_tls:
            tls_option["tls"] = ldap3.Tls(
                validate=ssl.CERT_NONE, version=version, ciphers="ALL:@SECLEVEL=0"
            )

        ldap_server = ldap3.Server(target_ip, get_info=ldap3.ALL, port=self._port, **tls_option)

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

                if result["result"] == "RESULT_STRONGER_AUTH_REQUIRED" and self._use_tls:
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

        self._ldap_server = ldap_server
        self._connection = ldap_connection

        self._default_search_base = self._ldap_server.info.other["defaultNamingContext"][0]
        self._domain = self._ldap_server.info.other["ldapServiceName"][0].split("@")[-1]

    @override
    def search(
        self,
        search_type: "LDAPObjectType | str" = LDAPObjectType.DEFAULT,
        search_base: str | None = None,
        search_filter: str | None = None,
        attributes: StrType | None = None,
        **kwargs: Any,
    ) -> list["LDAPEntry"]:
        """
        Run an LDAP search based on the provided parameters.

        Args:
            search_type (LDAPObjectType | str): Search type (see ldap_object_type.py for details)
            search_base (str | None)          : Search base (location in domain tree)
            search_filter (str | None)        : Search filter
            attributes (StrType | None)       : Attributes to include in the result
            **kwargs (Any)                    : Any other argument to pass

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
                raise ValueError(
                    f"{__class__.__name__}.ldap_entry_from_dict::Invalid entry provided"
                )

            return LDAPEntry(**entry)

        return list(
            map(
                ldap_entry_from_dict,
                filter(LDAPConnector.check_entry_type, results),
            )
        )

    def get_object(
        self,
        search_filter: str | None = None,
        attributes: StrType | None = None,
        search_base: str | None = None,
        auto: bool = False,
    ) -> dict[int | str, "LDAPObject"]:
        """
        Specific method to retrieve LDAP User instances.

        Args:
            search_filter (str)         : Filter to reduce search results
            attributes (str | List[str]): Attributes to include in result
            search_base (str)           : Where to base the search on in terms of directory location
            auto (bool)                 : Auto map the objects dynamically per type

        Returns:
            list[LDAPObject]: list of objects
        """

        entries = self.search(
            search_type=LDAPObjectType.DEFAULT,
            search_base=search_base,
            search_filter=search_filter,
            attributes=attributes,
        )

        def map_obj(entry: "LDAPEntry") -> "LDAPObject":
            if auto:
                obj_type = LDAPObjectType.from_object_cls(entry)
                LDAPDynamicObjectType = self._LDAP_PYTHON_CLS[obj_type.name].cls

                return LDAPDynamicObjectType(
                    self.complete_partial_entry(entry), self._DEFAULT_CAPABILITIES
                )

            return LDAPObject(entry, capabilities=self._DEFAULT_CAPABILITIES)

        return {obj.id: obj for obj in list(map(map_obj, entries))}

    def get_gpo(
        self, displayName: str = "*", name: StrType = "*", attributes: StrType | None = None
    ) -> dict[int | str, "LDAPGroupPolicyObject"]:
        """
        Specific method to retrieve LDAP GPO instances.

        Args:
            displayName (str)           : GPO display name
            name (StrType)              : GPO name
            attributes (str | list[str]): attributes to include in result

        Returns:
            list[LDAPGroupPolicyObject]: list of LDAPGroupPolicyObject instances
        """

        name = (
            f"(|{''.join([f'(name={link})' for link in name])})"
            if isinstance(name, list)
            else f"(name={name})"
        )

        entries = self.search(
            search_type=LDAPObjectType.GPO,
            search_base=None,
            search_filter=f"(&(displayName={displayName}){name}",
            attributes=attributes,
        )

        def map_gpo(entry: "LDAPEntry") -> "LDAPGroupPolicyObject":
            return LDAPGroupPolicyObject(entry, self._DEFAULT_CAPABILITIES)

        return {gpo.id: gpo for gpo in list(map(map_gpo, entries))}

    def get_subnet(
        self, search_filter: str | None = None, attributes: StrType | None = None
    ) -> dict[int | str, "LDAPSubnet"]:
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

        def map_net(entry: "LDAPEntry") -> "LDAPSubnet":
            return LDAPSubnet(entry, self._DEFAULT_CAPABILITIES)

        return {net.id: net for net in list(map(map_net, entries))}

    def get_computer(
        self,
        search_filter: str | None = None,
        attributes: StrType | None = None,
        search_base: str | None = None,
    ) -> dict[int | str, "LDAPComputer"]:
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

        def map_cpt(entry: "LDAPEntry") -> "LDAPComputer":
            return LDAPComputer(entry, capabilities=self._DEFAULT_CAPABILITIES)

        return {cpt.id: cpt for cpt in list(map(map_cpt, entries))}

    def get_user(
        self,
        search_filter: str | None = None,
        attributes: StrType | None = None,
        search_base: str | None = None,
    ) -> dict[int | str, "LDAPUser"]:
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

        def map_usr(entry: "LDAPEntry") -> "LDAPUser":
            return LDAPUser(entry, capabilities=self._DEFAULT_CAPABILITIES)

        return {usr.id: usr for usr in list(map(map_usr, entries))}

    def get_group(
        self,
        search_filter: str | None = None,
        search_base: str | None = None,
        attributes: StrType | None = None,
        recursive: bool = False,
    ) -> dict[int | str, "LDAPGroup"]:
        """
        Specific method to retrieve LDAP group objects.

        Args:
            search_filter (str)         : Filter to reduce search results
            attributes (str | List[str]): Attrbutes to include in result
            search_base (str)           : Where to base the search on in terms of directory location
            recursive (bool)            : Retrieve groups recursively if set to True

        Returns:
            list[LDAPGroup]: list of OU matching filter
        """

        entries = self.search(
            search_type=LDAPObjectType.GROUP,
            search_base=search_base,
            search_filter=search_filter,
            attributes=attributes,
        )

        def map_grp(entry: "LDAPEntry") -> "LDAPGroup":
            grp_instance = LDAPGroup(entry, self._DEFAULT_CAPABILITIES)
            if recursive:
                grp_instance.fetch_members(recursive)

            return grp_instance

        return {grp.id: grp for grp in list(map(map_grp, entries))}

    def get_ou(
        self,
        search_filter: str | None = None,
        search_base: str | None = None,
        attributes: StrType | None = None,
        recursive: bool = False,
    ) -> dict[int | str, "LDAPOrganizationalUnit"]:
        """
        Specific method to retrieve LDAP organizational unit objects.

        Args:
            dn (str):                   : Optional distinguished name to search
            search_filter (str)         : Filter to reduce search results
            attributes (str | List[str]): Attrbutes to include in result
            search_base (str)           : Where to base the search on in terms of directory location
            recursive (bool)            : Retrieve OUs recursively if set to True

        Returns:
            list[LDAPOrganizationalUnit]: list of OU matching filter
        """

        entries = self.search(
            search_type=LDAPObjectType.OU,
            search_base=search_base,
            search_filter=search_filter,
            attributes=attributes,
        )

        def map_ou(entry: "LDAPEntry") -> "LDAPOrganizationalUnit":
            ou_instance = LDAPOrganizationalUnit(entry, self._DEFAULT_CAPABILITIES)
            if recursive:
                ou_instance.fetch_objects(recursive)

            return ou_instance

        return {ou.id: ou for ou in list(map(map_ou, entries))}

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
            search_type=LDAPObjectType.from_object_cls(ldap_entry),
            search_filter=f"(distinguishedName={ldap_entry.dn})",
        )[0]

    def get_domain_admins(self) -> dict[int | str, "LDAPUser"]:
        """
        Return a list of the domain and enterprise admins.

        Returns:
            List[LDAPEntry]: a list of LDAPEntry instances representing the domain admins
        """

        return self.get_user(
            search_filter="(&(objectClass=user)(objectCategory=Person)(adminCount=1))",
        )

    def ldap_object_opt_from_obj_type(self, ldap_obj_type_name: str) -> "LDAPObjectOptions":
        """
        Return an LDAP object based on a given LDAPEntry.

        Args:
            ldap_obj_type_name (str): The LDAPObjectType element name

        Returns:
            LDAPObjTypeAlias: the python class matching the provided entry
        """

        return self._LDAP_PYTHON_CLS[ldap_obj_type_name]

    # ****************************************************************
    # Static methods

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
