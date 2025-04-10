import socket
import ssl
from typing import TYPE_CHECKING, Dict, List, Union

import ldap3

from oudjat.connectors import Connector
from oudjat.utils import ColorPrint

from .objects.ldap_entry import LDAPEntry
from .objects.ldap_object import LDAPObject
from .objects.ldap_object_types import LDAPObjectType, get_ldap_class

if TYPE_CHECKING:
    from .objects.account.group.ldap_group import LDAPGroup
    from .objects.account.ldap_computer import LDAPComputer
    from .objects.account.ldap_user import LDAPUser
    from .objects.gpo.ldap_gpo import LDAPGroupPolicyObject
    from .objects.ou.ldap_ou import LDAPOrganizationalUnit
    from .objects.subnet.ldap_subnet import LDAPSubnet


class LDAPConnector(Connector):
    """
    LDAP connector to interact and query LDAP servers
    """

    # ****************************************************************
    # Attributes & Constructors

    def __init__(
        self, server: str, service_name: str = "OudjatLDAPConnection", use_tls: bool = False
    ) -> None:
        """
        Constructor

        Args:
            server (str)        : server name
            service_name (str)  : service name used to store credentials
            use_tls (bool)      : should the connector use TLS for LDAPS connection
        """

        self.use_tls = use_tls
        self.port = 389
        if use_tls:
            self.port = 636

        super().__init__(target=server, service_name=service_name, use_credentials=True)

        self.default_search_base: str = None
        self.ldap_server: ldap3.Server = None
        self.connection: ldap3.Connection = None
        self.domain: str = None

    # ****************************************************************
    # Methods

    def get_domain(self) -> str:
        """
        Getter for AD domain

        Returns:
            str : domain name
        """

        return self.domain

    def get_connection(self) -> ldap3.Connection:
        """
        Getter for the server connection

        Returns:
            ldap3.Connection : active connection
        """

        return self.connection

    def get_default_search_base(self) -> str:
        """
        Getter for the default search base

        Returns:
            str : default domain search base
        """

        return self.default_search_base

    def set_tls_usage(self, use_tls: bool = True) -> None:
        """
        Setter for connector tls usage

        Args:
            use_tls (bool) : should the connector use TLS
        """

        self.use_tls = use_tls
        if use_tls:
            self.port = 636

        else:
            self.port = 389

    def connect(self, version: ssl._SSLMethod = None) -> None:
        """
        Initiate connection to target server

        Args:
            version (ssl._SSLMethod) : SSL/TLS version
        """

        if version is None:
            try:
                self.connect(version=ssl.PROTOCOL_TLSv1_2)

            except ldap3.core.exceptions.LDAPSocketOpenError as e:
                if not self.use_tls:
                    ColorPrint.yellow(f"Got error while trying to connect to LDAP: {e}")

                self.connect(version=ssl.PROTOCOL_TLSv1)

            return

        target_ip = socket.gethostbyname(self.target)

        if not target_ip:
            raise Exception(f"The target {self.target} is unreachable")

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
                        "LDAP channel binding required. Use -scheme ldaps -ldap-channel-binding"
                    )

                raise Exception(
                    f"Failed LDAP authentication ({result['description']}) {result['message']}]"
                )

        if ldap_server.schema is None:
            ldap_server.get_info_from_server(ldap_connection)

            if ldap_connection.result["result"] != 0:
                if ldap_connection.result["message"].split(":")[0] == "000004DC":
                    raise Exception(
                        "Failed to bind to LDAP. Most likely due to an invalid username"
                    )

            if ldap_server.schema is None:
                raise Exception("Failed to get LDAP schema")

        ColorPrint.green(f"Bound to {ldap_server}")

        self.ldap_server = ldap_server
        self.connection = ldap_connection

        self.default_search_base = self.ldap_server.info.other["defaultNamingContext"][0]
        self.domain = self.ldap_server.info.other["ldapServiceName"][0].split("@")[-1]

    # TODO: use LDAPObjectType for search type
    def search(
        self,
        search_type: str = "DEFAULT",
        search_base: str = None,
        search_filter: str = None,
        attributes: Union[str, List[str]] = None,
        **kwargs,
    ) -> List[LDAPEntry]:
        """
        Runs an LDAP search based on the provided parameters

        Args:
            search_type (str)            : search type (see ldap_object_type.py for details)
            search_base (str)            : search base (location in domain tree)
            search_filter (str)          : search filter
            attributes (str | List[str]) : attributes to include in the result
            **kwargs (Dict)              : any other argument to pass

        Returns:
            List[LDAPEntry] : list of ldap entries
        """

        if self.connection is None:
            raise ConnectionError(
                f"You must initiate connection to {self.target} before running search !"
            )

        search_type = search_type.upper()
        if search_type not in LDAPObjectType.__members__:
            raise ValueError(f"Invalid search type proviced: {search_type}")

        if search_base is None:
            search_base = self.default_search_base

        # INFO: If the search type is default : final filter is equal to provided search filter
        # Else final filter is a combination of filter matching search type + provided search filter
        formated_filter = LDAPObjectType[search_type].value.get("filter", "")
        if search_type.lower() == "default" and search_filter is not None:
            formated_filter = search_filter

        else:
            if search_filter:
                formated_filter = f"(&{formated_filter}{search_filter})"

        if attributes is None:
            attributes = LDAPObjectType[search_type].value.get("attributes", "*")

        results = self.connection.extend.standard.paged_search(
            search_base=search_base,
            search_filter=formated_filter,
            attributes=attributes,
            generator=False,
            **kwargs,
        )

        entries = list(
            map(
                LDAPConnector.ldap_entry_from_dict,
                filter(LDAPConnector.check_entry_type, results),
            )
        )

        return entries

    def get_mapped_object(
        self,
        search_type: LDAPObjectType,
        search_base: str = None,
        search_filter: str = None,
        attributes: Union[str, List[str]] = None,
    ) -> List["LDAPObject"]:
        """
        Generitc method to generate LDAPObject instances based on an LDAP entry search result

        Args:
            search_filter (str)          : filter to reduce search results
            attributes (str | List[str]) : attributes to include in result
            search_base (str)            : where to base the search on in terms of directory location

        Returns:
            List[LDAPComputer] : list of computers
        """

        entries = self.search(
            search_type=search_type.name,
            search_base=search_base,
            search_filter=search_filter,
            attributes=attributes,
        )

        ldap_obj_cls = search_type.value.get("pythonClass")
        return self.map_entries(entries, ldap_cls=ldap_obj_cls)

    def get_gpo(
        self, displayName: str = "*", name: str = "*", attributes: Union[str, List[str]] = None
    ) -> List["LDAPGroupPolicyObject"]:
        """
        Specific method to retreive LDAP GPO instances

        Args:
            displayName (str)            : GPO display name
            name (str)                   : GPO name
            attributes (str | List[str]) : attributes to include in result

        Returns:
            List[LDAPGroupPolicyObject] : list of LDAPGroupPolicyObject instances
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
        Specific method to retreive LDAP subnet instances

        Args:
            search_filter (str) : filter to reduce search results
            attributes (str | List[str]) : attributes to include in result

        Returns:
            List[LDAPSubnet] : list of subnets
        """

        sb_dc = ','.join([f"DC={dc.lower()}" for dc in self.domain.split(".")])

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
        Specific method to retreive LDAP Computer instances

        Args:
            search_filter (str)          : filter to reduce search results
            attributes (str | List[str]) : attributes to include in result
            search_base (str)            : where to base the search on in terms of directory location

        Returns:
            List[LDAPComputer] : list of computers
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
        Specific method to retreive LDAP User instances

        Args:
            search_filter (str)          : filter to reduce search results
            attributes (str | List[str]) : attributes to include in result
            search_base (str)            : where to base the search on in terms of directory location

        Returns:
            List[LDAPUser] : list of users
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
        Retreives and returns the members of the given group

        Args:
            ldap_group (LDAPGroup)  : group to retreive members from
            recursive (bool)        : wheither to retrieve members recursively or not

        Returns:
            List[LDAPObject] : list of members
        """

        members = []
        for ref in ldap_group.get_member_refs():
            # INFO: Search for the ref in LDAP server
            # TODO: Must implement an LDAPFilter class to handle potential escape characters
            escaped_ref = ldap3.utils.conv.escape_filter_chars(ref)
            ref_search = self.search(search_filter=f"(distinguishedName={escaped_ref})")

            if len(ref_search) > 0:
                ref_search: LDAPEntry = ref_search[0]
                obj_class = ref_search.get_type()

                new_member: "LDAPObject" = get_ldap_class(obj_class)(ldap_entry=ref_search)

                if new_member.get_type() == "GROUP" and recursive:
                    new_member.get_members(ldap_connector=self, recursive=recursive)

                members.append(new_member)

        return members

    def is_object_member_of(
        self, ldap_object: "LDAPObject", ldap_group: "LDAPGroup", extended: bool = False
    ) -> bool:
        """
        Checks wheither the given object is member of the giver group

        Args:
            ldap_object (LDAPObject) : object to check membership of
            ldap_group (LDAPGroup)   : group to check object membership

        Returns:
            bool : wheither the object is a member of the group or not
        """

        member_ref_list = None

        if extended:
            member_ref_list = ldap_group.get_members_flat(ldap_connector=self)

        else:
            member_ref_list = ldap_group.members.values()

        return ldap_object.get_uuid() in [m.get_id() for m in member_ref_list]

    def get_ou(
        self,
        search_filter: str = None,
        search_base: str = None,
        attributes: Union[str, List[str]] = None,
    ) -> List["LDAPOrganizationalUnit"]:
        """
        Specific method to retrieve LDAP organizational unit objects

        Args:
            search_filter (str)          : filter to reduce search results
            attributes (str | List[str]) : attrbutes to include in result
            search_base (str)            : where to base the search on in terms of directory location

        Returns:
            List["LDAPOrganizationalUnit"] : list of OU matching filter
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
        Returns members of a given OU
        """

        search_args = {"search_base": ldap_ou.get_dn()}

        if object_types is not None:
            types_filter_str = ''.join([f"(objectClass={t})" for t in object_types])
            search_args["search_filter"] = f"(|{types_filter_str})"

        return self.search(**search_args)

    # ****************************************************************
    # Static methods

    @staticmethod
    def map_entries(entries: List["LDAPEntry"], ldap_cls: "LDAPObject") -> List["LDAPObject"]:
        """
        Maps a list of ldap entries to a list of the provided LDAP class

        Args:
            entries (List[LDAPEntry]) : list of entries to map
            ldap_cls (LDAPObject)     : ldap class used to map

        Returns:
            List[LDAPObject] : mapped list of ldap object
        """

        if not issubclass(ldap_cls, LDAPObject):
            raise ValueError("Invalid class provided. Please provide a valid LDAPObject instance")

        return list(map(lambda entry: ldap_cls(ldap_entry=entry), entries))

    @staticmethod
    def check_entry_type(entry: Dict) -> bool:
        """
        Checks if the provided entry is a searchResEntry
        """
        return entry["type"] == "searchResEntry"

    def ldap_entry_from_dict(entry: Dict) -> "LDAPEntry":
        """
        Creates an LDAPEntry from the provided dictionary
        """

        if entry.get("attributes", None) is None:
            raise ValueError("LDAPConnector.ldap_entry_from_dict::Invalid entry provided")

        return LDAPEntry(**entry)
