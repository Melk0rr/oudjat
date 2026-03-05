"""Main module of the LDAP package. Handles connection to an LDAP server and data retrieving operations."""

import logging
import socket
import ssl
from enum import IntEnum
from typing import Any, TypedDict, final, override

import ldap3
from ldap3.core.exceptions import LDAPSocketOpenError

from oudjat.utils import Context
from oudjat.utils.credentials import NoCredentialsError
from oudjat.utils.types import DataType, StrType

from ..connector import Connector
from .exceptions import (
    InvalidLDAPEntryError,
    LDAPConnectionError,
    LDAPSchemaError,
    LDAPUnreachableServerError,
)
from .ldap_filter import LDAPFilter, LDAPFilterStrFormat
from .objects import (
    LDAPCapabilities,
    LDAPComputer,
    LDAPGroup,
    LDAPGroupPolicyObject,
    LDAPObject,
    LDAPObjectOptions,
    LDAPOrganizationalUnit,
    LDAPSubnet,
    LDAPUser,
)
from .objects.account import LDAPComputerFlag, LDAPUserFlag
from .objects.ldap_entry import LDAPEntry
from .objects.ldap_object_types import LDAPObjectType


class LDAPTLSVersion(IntEnum):
    """
    A helper enumeration to describe TLS versions.
    """

    TLSv1 = ssl.PROTOCOL_TLSv1
    TLSv1_1 = ssl.PROTOCOL_TLSv1_1
    TLSv1_2 = ssl.PROTOCOL_TLSv1_2

    @override
    def __str__(self) -> str:
        """
        Convert an LDAPTLSVersion into a string.

        Returns:
            str: A string representation of the LDAPTLSVersion
        """

        return self._name_


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
        self,
        target: str,
        username: str | None = None,
        password: str | None = None,
        use_tls: bool = True,
        is_active_directory: bool = True,
    ) -> None:
        """
        Create a new LDAPConnector.

        Args:
            target (str)             : Server name
            username (str)           : Username to use for the connection
            password (str)           : Password to use for the connection
            service_name (str)       : Service name used to store credentials
            use_tls (bool)           : Should the connector use TLS for LDAPS connection
            is_active_directory(bool): Indicates if the target directory is an MS Active Directory. Defaults to True
        """

        self._use_tls: bool = use_tls
        self._port: "LDAPPort" = LDAPPort.TLS if use_tls else LDAPPort.DEFAULT

        super().__init__(target=target, username=username, password=password)

        self.logger = logging.getLogger(__name__)

        self._domain: str = ""
        self._default_search_base: str = ""

        self._ldap_server: ldap3.Server
        self._connection: ldap3.Connection | None = None

        context = Context()

        self.logger.debug(f"{context}::New LDAPConnector - {self._target}:{self._port}")

        self._is_active_directory: bool = is_active_directory

        self._CAPABILITIES: "LDAPCapabilities" = LDAPCapabilities(
            ldap_search=self.fetch,
            ldap_obj_opt=self._object_opt,
        )

    # ****************************************************************
    # Methods - getters/setters

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

    # ****************************************************************
    # Methods - access

    def set_tls_usage(self, use_tls: bool = True) -> None:
        """
        Set the TLS usage.

        Args:
            use_tls (bool): should the connector use TLS
        """

        self._use_tls = use_tls
        self._port = LDAPPort.TLS if use_tls else LDAPPort.DEFAULT

        self.logger.debug(f"{Context()}::New TLS usage: {self._use_tls}({self._port})")

    @override
    def connect(self, version: "LDAPTLSVersion | None" = None) -> None:
        """
        Initiate connection to target server.

        Args:
            version (ssl._SSLMethod): SSL/TLS version

        Raises:
            NoCredentialsError        : No credentials were provided to connect to the server
            LDAPSocketOpenError       : An error occured while bounding TLS socket
            LDAPUnreachableServerError: The LDAP server is unreachable
            LDAPConnectionError       : Wrong LDAP credentials were provided
            LDAPSchemaError           : Failed to retrieve LDAP server schema
        """

        context = Context()

        if self._credentials is None:
            raise NoCredentialsError(
                f"{context}::Cannot connect to {self._target}, no credentials provided"
            )

        if version is None:
            self.logger.debug(
                f"{context}::No TLS version specified, trying with {LDAPTLSVersion.TLSv1_2}"
            )

            try:
                self.connect(version=LDAPTLSVersion.TLSv1_2)

            except LDAPSocketOpenError as e:
                if not self._use_tls:
                    self.logger.warning(f"Error while trying to connect to LDAP: {e}")

                self.connect(version=LDAPTLSVersion.TLSv1)

            return

        target_ip = socket.gethostbyname(str(self._target))
        if not target_ip:
            raise LDAPUnreachableServerError(f"{context}::The target {self.target} is unreachable")

        TLSOption = TypedDict("TLSOption", {"use_ssl": bool, "tls": ldap3.Tls | None})
        tls_option: TLSOption = {"use_ssl": self._use_tls, "tls": None}

        if self._use_tls:
            tls_option["tls"] = ldap3.Tls(
                validate=ssl.CERT_NONE, version=version, ciphers="ALL:@SECLEVEL=0"
            )

        ldap_server = ldap3.Server(target_ip, get_info=ldap3.ALL, port=self._port, **tls_option)
        ldap_connection = ldap3.Connection(
            ldap_server,
            user=self._credentials.username,
            password=self._credentials.password,
            auto_referrals=False,
            authentication=ldap3.NTLM,
        )

        if not ldap_connection.bound:
            self.logger.debug(f"{context}::Bounding connection")
            bind_result = ldap_connection.bind()

            if not bind_result:
                result = ldap_connection.result

                if result["result"] == "RESULT_STRONGER_AUTH_REQUIRED" and self._use_tls:
                    self.logger.debug(f"{context}::Stronger LDAP authentication is required.")

                    self.set_tls_usage(use_tls=True)
                    return self.connect()

                if (
                    result["description"] == "invalidCredentials"
                    and result["message"].split(":")[0] == "80090346"
                ):
                    raise LDAPConnectionError(
                        f"{context}::LDAP channel binding required. Use -scheme ldaps -ldap-channel-binding"
                    )

                raise LDAPConnectionError(
                    f"{context}::Failed LDAP authentication ({result['description']}) {result['message']}]"
                )

        if ldap_server.schema is None:
            ldap_server.get_info_from_server(ldap_connection)

            if ldap_connection.result["result"] != 0:
                if ldap_connection.result["message"].split(":")[0] == "000004DC":
                    raise LDAPConnectionError(
                        f"{context}::Failed to bind to LDAP. Most likely due to an invalid username"
                    )

            if ldap_server.schema is None:
                raise LDAPSchemaError(f"{context}::Failed to get LDAP schema")

        self.logger.info(f"Bound to {ldap_server}")

        self._ldap_server = ldap_server
        self._connection = ldap_connection

        self._default_search_base = self._ldap_server.info.other["defaultNamingContext"][0]
        self._domain = self._ldap_server.info.other["ldapServiceName"][0].split("@")[-1]

        self.logger.debug(
            f"{context}::Default search base for {self._domain} is {self._default_search_base}"
        )

    @override
    def fetch(
        self,
        search_type: "LDAPObjectType" = LDAPObjectType.DEFAULT,
        search_base: str | None = None,
        search_filter: "LDAPFilter | str | None" = None,
        attributes: "StrType | None" = None,
        payload: dict[str, Any] | None = None,
    ) -> list["LDAPEntry"]:
        """
        Run an LDAP search based on the provided parameters.

        Args:
            search_type (LDAPObjectType | str): Search type (see ldap_object_type.py for details)
            search_base (str | None)          : Search base (location in domain tree)
            search_filter (str | None)        : Search filter
            attributes (StrType | None)       : Attributes to include in the result
            payload (dict[str, Any] | None)   : Payload to send to the server

        Returns:
            list[LDAPEntry]: list of ldap entries

        Raises:
            LDAPConnectionError: No connection was previously initiated
        """

        context = Context()
        if self.connection is None:
            raise LDAPConnectionError(
                f"{context}::You must initiate connection to {self.target} before running search !"
            )

        self.logger.info(f"Fetching {search_type} from {self.domain}")

        if payload is None:
            payload = {}

        payload["generator"] = False

        # If the search type is default : final filter is equal to provided search filter
        # Else final filter is a combination of filter matching search type + provided search filter
        formated_filter = search_type.filter
        if search_type == LDAPObjectType.DEFAULT and search_filter is not None:
            formated_filter = search_filter

        elif search_filter is not None:
            if not isinstance(search_filter, LDAPFilter):
                search_filter = LDAPFilter(search_filter)

            formated_filter = formated_filter & search_filter

        payload["search_filter"] = str(formated_filter)
        payload["search_base"] = search_base or self.default_search_base

        attributes_complete = []
        attributes_complete.extend(search_type.attributes)

        if self._is_active_directory and search_type.ad_attributes:
            attributes_complete.extend(search_type.ad_attributes)

        if attributes is not None:
            attributes_complete.extend(attributes)

        payload["attributes"] = list(set(attributes_complete))

        self.logger.debug(f"{context}::{search_type} > {payload}")

        # Actual request
        results = self.connection.extend.standard.paged_search(**payload)

        def ldap_entry_from_dict(entry: dict[str, Any]) -> "LDAPEntry":
            if entry.get("attributes", None) is None:
                raise InvalidLDAPEntryError(
                    f"{context}::Invalid entry provided. No attribute found"
                )

            return LDAPEntry(**entry)

        res = list(
            map(
                ldap_entry_from_dict,
                filter(LDAPConnector._check_search_res_entry, results),
            )
        )

        self.logger.debug(f"{context}::{search_type} > {[el.dn for el in res]}")
        self.logger.debug(f"{context}::Retrieved {len(res)} entries")

        return res

    # ****************************************************************
    # Methods - ldap objects

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
                cls=LDAPObject, fetch=self.ldap_objects
            ),
            f"{LDAPObjectType.COMPUTER}": LDAPObjectOptions["LDAPComputer"](
                cls=LDAPComputer, fetch=self.ldap_computers
            ),
            f"{LDAPObjectType.GPO}": LDAPObjectOptions["LDAPGroupPolicyObject"](
                cls=LDAPGroupPolicyObject, fetch=self.ldap_gpos
            ),
            f"{LDAPObjectType.GROUP}": LDAPObjectOptions["LDAPGroup"](
                cls=LDAPGroup, fetch=self.ldap_groups
            ),
            f"{LDAPObjectType.OU}": LDAPObjectOptions["LDAPOrganizationalUnit"](
                cls=LDAPOrganizationalUnit, fetch=self.ldap_ous
            ),
            f"{LDAPObjectType.SUBNET}": LDAPObjectOptions["LDAPSubnet"](
                cls=LDAPSubnet, fetch=self.ldap_subnets
            ),
            f"{LDAPObjectType.USER}": LDAPObjectOptions["LDAPUser"](
                cls=LDAPUser, fetch=self.ldap_users
            ),
        }

        return obj_map[f"{ldap_obj_type}"]

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

        def _map_obj(entry: "LDAPEntry") -> "LDAPObject":
            if auto:
                obj_type = LDAPObjectType.from_object_cls(entry)
                LDAPDynamicObjectType = self._object_opt(obj_type).cls

                return LDAPDynamicObjectType(self.complete_partial_entry(entry), self._CAPABILITIES)

            return LDAPObject(entry, capabilities=self._CAPABILITIES)

        objects = {obj.dn: obj for obj in list(map(_map_obj, entries))}

        return objects

    def ldap_computers(self, entries: list["LDAPEntry"]) -> dict[str, "LDAPComputer"]:
        """
        Map the provided LDAP entries into a dictionary of LDAPComputer instances.

        Args:
            entries (list[LDAPEntry]): LDAP entries to map

        Returns:
            dict[str, LDAPComputer]: Mapped entries as a dictionary of LDAP computers
        """

        def _map_cpt(entry: "LDAPEntry") -> "LDAPComputer":
            cpt = LDAPComputer(entry, capabilities=self._CAPABILITIES)
            cpt.flags.update(LDAPComputerFlag.flags(cpt))

            return cpt

        computers = {cpt.dn: cpt for cpt in list(map(_map_cpt, entries))}

        return computers

    def ldap_users(self, entries: list["LDAPEntry"]) -> dict[str, "LDAPUser"]:
        """
        Map the provided LDAP entries into a dictionary of User instances.

        Args:
            entries (list[LDAPEntry]): LDAP entries to map

        Returns:
            dict[str, LDAPUser]: Mapped entries as a dictionary of LDAP computers
        """

        def _map_usr(entry: "LDAPEntry") -> "LDAPUser":
            usr = LDAPUser(entry, capabilities=self._CAPABILITIES)
            usr.flags.update(LDAPUserFlag.flags(usr))

            return usr

        users = {usr.dn: usr for usr in list(map(_map_usr, entries))}

        return users

    def ldap_groups(
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

        def _map_grp(entry: "LDAPEntry") -> "LDAPGroup":
            grp_instance = LDAPGroup(entry, self._CAPABILITIES)
            if recursive:
                grp_instance.fetch_members(recursive)

            return grp_instance

        groups = {grp.dn: grp for grp in list(map(_map_grp, entries))}

        return groups

    def ldap_gpos(self, entries: list["LDAPEntry"]) -> dict[str, "LDAPGroupPolicyObject"]:
        """
        Map the provided LDAP entries into a dictionary of LDAPGroupPolicyObject instances.

        Args:
            entries (list[LDAPEntry]): LDAP entries to map

        Returns:
            dict[str, LDAPGroup]: Mapped entries as a dictionary of LDAP gpos
        """

        def _map_gpo(entry: "LDAPEntry") -> "LDAPGroupPolicyObject":
            return LDAPGroupPolicyObject(entry, self._CAPABILITIES)

        gpos = {gpo.dn: gpo for gpo in list(map(_map_gpo, entries))}

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

        def _map_ou(entry: "LDAPEntry") -> "LDAPOrganizationalUnit":
            ou_instance = LDAPOrganizationalUnit(entry, self._CAPABILITIES)
            if recursive:
                ou_instance.fetch_objects(recursive)

            return ou_instance

        ous = {ou.dn: ou for ou in list(map(_map_ou, entries))}

        return ous

    def ldap_subnets(self, entries: list["LDAPEntry"]) -> dict[str, "LDAPSubnet"]:
        """
        Map the provided LDAP entries into a dictionary of LDAPSubnet instances.

        Args:
            entries (list[LDAPEntry]): LDAP entries to map

        Returns:
            dict[str, LDAPSubnet]: Mapped entries as a dictionary of LDAP ous
        """

        self.logger.info(f"Mapping {len(entries)} entries into LDAPSubnets")

        def _map_net(entry: "LDAPEntry") -> "LDAPSubnet":
            return LDAPSubnet(entry, self._CAPABILITIES)

        subnets = {net.dn: net for net in list(map(_map_net, entries))}

        return subnets

    # ****************************************************************
    # Methods - core

    def objects(
        self,
        search_filter: "LDAPFilter | str | None" = None,
        attributes: "StrType | None" = None,
        search_base: str | None = None,
        payload: dict[str, Any] | None = None,
    ) -> "DataType":
        """
        Return generic LDAP object data.

        Filters no object class nor categories.
        First convert found entries into LDAPObject instances to compute some values.

        Args:
            search_filter (str)            : LDAP Filter to reduce search results
            attributes (str | list[str])   : Additional attributes to include in result
            search_base (str)              : Where to base the search on in terms of directory location
            payload (dict[str, Any] | None): Payload to send to the server

        Returns:
            DataType: A list of entries based on the provided arguments and payload
        """

        entries = self.fetch(
            search_type=LDAPObjectType.DEFAULT,
            search_base=search_base,
            search_filter=search_filter,
            attributes=attributes,
            payload=payload,
        )

        self.logger.info(f"Processing {len(entries)} generic object entries...")

        # Processing raw LDAP entries into LDAP object instances
        def _obj_dict(e: "LDAPEntry") -> dict[str, Any]:
            return LDAPObject(e, capabilities=self._CAPABILITIES).to_dict()

        processed = list(map(_obj_dict, entries))
        return processed

    def computers(
        self,
        search_filter: "LDAPFilter | str | None" = None,
        attributes: "StrType | None" = None,
        search_base: str | None = None,
        payload: dict[str, Any] | None = None,
    ) -> "DataType":
        """
        Specific method to retrieve LDAP Computer instances.

        First convert found entries into LDAPComputer instances to compute some values.

        Args:
            search_filter (str)            : LDAP Filter to reduce search results
            attributes (str | list[str])   : Additional attributes to include in result
            search_base (str)              : where to base the search on in terms of directory location
            payload (dict[str, Any] | None): Payload to send to the server

        Returns:
            DataType: A list of entries based on the provided arguments and payload
        """

        entries = self.fetch(
            search_type=LDAPObjectType.COMPUTER,
            search_base=search_base,
            search_filter=search_filter,
            attributes=attributes,
            payload=payload,
        )

        self.logger.info(f"Processing {len(entries)} computer entries...")

        # Processing raw LDAP entries into LDAP computer instances
        def _cpt_dict(e: "LDAPEntry") -> dict[str, Any]:
            cpt = LDAPComputer(e, capabilities=self._CAPABILITIES)
            cpt.flags.update(LDAPComputerFlag.flags(cpt))

            return cpt.to_dict()

        processed = list(map(_cpt_dict, entries))
        return processed

    def users(
        self,
        search_filter: "LDAPFilter | str | None" = None,
        attributes: "StrType | None" = None,
        search_base: str | None = None,
        payload: dict[str, Any] | None = None,
        extension_attr: bool = True,
    ) -> "DataType":
        """
        Return LDAP user data.

        First convert the found entries into LDAPUser instances in order to compute some values.

        Args:
            search_filter (str)            : LDAP Filter to reduce search results
            attributes (str | list[str])   : Additional attributes to include in result
            search_base (str)              : Where to base the search on in terms of directory location
            payload (dict[str, Any] | None): Payload to send to the server
            extension_attr (bool)          : Whether to include extension attributes

        Returns:
            DataType: A list of entries based on the provided arguments and payload
        """

        if extension_attr:
            if attributes is None:
                attributes = []

            if not isinstance(attributes, list):
                attributes = [attributes]

            attributes.extend([f"extensionAttribute{i}" for i in range(1, 16)])
            attributes = list(set(attributes))

        entries = self.fetch(
            search_type=LDAPObjectType.USER,
            search_base=search_base,
            search_filter=search_filter,
            attributes=attributes,
            payload=payload,
        )

        self.logger.info(f"Processing {len(entries)} user entries...")

        # Processing raw LDAP entries into LDAP user instances
        def _usr_dict(e: "LDAPEntry") -> dict[str, Any]:
            usr = LDAPUser(e, capabilities=self._CAPABILITIES)
            usr.flags.update(LDAPUserFlag.flags(usr))

            return usr.to_dict()

        processed = list(map(_usr_dict, entries))
        return processed

    # TODO: Add more options to retrieve different levels of members.
    def groups(
        self,
        search_filter: "LDAPFilter | str | None" = None,
        search_base: str | None = None,
        attributes: "StrType | None" = None,
        payload: dict[str, Any] | None = None,
    ) -> "DataType":
        """
        Return LDAP group data.

        First convert found entries into LDAPGroup instances to compute some values.

        Args:
            search_filter (str)            : LDAP Filter to reduce search results
            attributes (str | list[str])   : Additional attributes to include in result
            search_base (str)              : Where to base the search on in terms of directory location
            payload (dict[str, Any] | None): Payload to send to the server

        Returns:
            DataType: A list of entries based on the provided arguments and payload
        """

        entries = self.fetch(
            search_type=LDAPObjectType.GROUP,
            search_base=search_base,
            search_filter=search_filter,
            attributes=attributes,
            payload=payload,
        )

        self.logger.info(f"Processing {len(entries)} group entries...")

        # Processing raw LDAP entries into LDAP group instances
        def _grp_dict(e: "LDAPEntry") -> dict[str, Any]:
            return LDAPGroup(e, capabilities=self._CAPABILITIES).to_dict()

        processed = list(map(_grp_dict, entries))
        return processed

    def gpos(
        self,
        displayName: str = "*",
        name: "StrType" = "*",
        search_filter: "LDAPFilter | str | None" = None,
        search_base: str | None = None,
        attributes: "StrType | None" = None,
        payload: dict[str, Any] | None = None,
    ) -> "DataType":
        """
        Return GPOs data.

        First convert found entries into LDAPGroupPolicyObject instances to compute some values.

        Args:
            displayName (str)                      : GPO display name
            name (StrType)                         : GPO name (link)
            search_filter (str | LDAPFilter | None): LDAP Filter to reduce search results
            search_base (str)                      : Where to base the search on in terms of directory location
            attributes (str | list[str])           : Attributes to include in result
            payload (dict[str, Any] | None)        : Payload to send to the server

        Returns:
            DataType: A list of entries based on the provided arguments and payload
        """

        name_filter = LDAPFilter()
        if isinstance(name, list):
            name_filter.set_operator_from_str("|")

            for link in name:
                name_filter.add_node(LDAPFilter(f"(name={link})"))

        else:
            name_filter = LDAPFilter(f"(name={name})")

        entries_filter = LDAPFilter(f"(displayName={displayName})") & name_filter

        if search_filter:
            if not isinstance(search_filter, LDAPFilter):
                search_filter = LDAPFilter(search_filter)

            entries_filter = entries_filter & search_filter

        entries = self.fetch(
            search_type=LDAPObjectType.GPO,
            search_base=search_base,
            search_filter=entries_filter,
            attributes=attributes,
            payload=payload,
        )

        self.logger.info(f"Processing {len(entries)} gpo entries...")

        # Processing raw LDAP entries into LDAP gpo instances
        def _gpo_dict(e: "LDAPEntry") -> dict[str, Any]:
            return LDAPGroupPolicyObject(e, capabilities=self._CAPABILITIES).to_dict()

        processed = list(map(_gpo_dict, entries))
        return processed

    def ous(
        self,
        search_filter: "LDAPFilter | str | None" = None,
        search_base: str | None = None,
        attributes: "StrType | None" = None,
        payload: dict[str, Any] | None = None,
    ) -> "DataType":
        """
        Return OU data.

        First convert found entries into LDAPOrganizationalUnit instances to compute some values.

        Args:
            dn (str):                       : Optional distinguished name to search
            search_filter (str | LDAPFilter): LDAP Filter to reduce search results
            attributes (str | list[str])    : Additional attributes to include in result
            search_base (str)               : Where to base the search on in terms of directory location
            payload (dict[str, Any] | None) : Payload to send to the server

        Returns:
            DataType: A list of entries based on the provided arguments and payload
        """

        entries = self.fetch(
            search_type=LDAPObjectType.OU,
            search_base=search_base,
            search_filter=search_filter,
            attributes=attributes,
            payload=payload,
        )

        self.logger.info(f"Processing {len(entries)} ou entries...")

        # Processing raw LDAP entries into LDAP ous instances
        def _ou_dict(e: "LDAPEntry") -> dict[str, Any]:
            return LDAPOrganizationalUnit(e, capabilities=self._CAPABILITIES).to_dict()

        processed = list(map(_ou_dict, entries))
        return processed

    def subnets(
        self,
        search_filter: "LDAPFilter | str | None" = None,
        attributes: "StrType | None" = None,
        payload: dict[str, Any] | None = None,
    ) -> "DataType":
        """
        Return LDAP subnet data.

        First convert found entries into LDAPSubnet instances to compute some values.

        Args:
            search_filter (str)            : LDAP Filter to reduce search results
            attributes (str | list[str])   : Additional attributes to include in result
            payload (dict[str, Any] | None): Payload to send to the server

        Returns:
            DataType: A list of entries based on the provided arguments and payload
        """

        sb_dc = ",".join([f"DC={dc.lower()}" for dc in self.domain.split(".")])

        entries = self.fetch(
            search_type=LDAPObjectType.SUBNET,
            search_base=f"CN=Subnets,CN=Sites,CN=Configuration,{sb_dc}",
            search_filter=search_filter,
            attributes=attributes,
            payload=payload,
        )

        self.logger.info(f"Processing {len(entries)} subnet entries...")

        # Processing raw LDAP entries into LDAP subnet instances
        def _net_dict(e: "LDAPEntry") -> dict[str, Any]:
            return LDAPSubnet(e, capabilities=self._CAPABILITIES).to_dict()

        processed = list(map(_net_dict, entries))
        return processed

    def complete_partial_entry(self, ldap_entry: "LDAPEntry") -> "LDAPEntry":
        """
        Completes a partial LDAP entry by searching for the full details of the entry in the LDAP directory.

        This method takes an `LDAPEntry` object and performs a search operation to fetch the complete details of the entry.
        The search is conducted using the distinguished name (DN) of the provided `LDAPEntry`.

        Args:
            ldap_entry (LDAPEntry): An object representing a partial entry in the LDAP directory.

        Returns:
            LDAPEntry: A complete LDAP entry that matches the provided partial entry, including all details found in the search operation.
        """

        return self.fetch(
            search_type=LDAPObjectType.from_object_cls(ldap_entry),
            search_filter=LDAPFilterStrFormat.DN(ldap_entry.dn),
        )[0]

    def domain_admins(self) -> "DataType":
        """
        Return a list of the domain and enterprise admins.

        Returns:
            DataType: a list of LDAPEntry instances representing the domain admins
        """

        return self.users(
            search_filter="(&(objectClass=user)(objectCategory=Person)(adminCount=1))",
        )

    # ****************************************************************
    # Static methods

    @staticmethod
    def _check_search_res_entry(entry: dict[str, Any]) -> bool:
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
            raise InvalidLDAPEntryError(f"{Context()}::Invalid entry provided")

        return LDAPEntry(**entry)
