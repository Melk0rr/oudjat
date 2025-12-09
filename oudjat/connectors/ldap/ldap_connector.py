"""Main module of the LDAP package. Handles connection to an LDAP server and data retrieving operations."""

import logging
import socket
import ssl
from enum import IntEnum
from typing import Any, TypedDict, final, override

import ldap3
from ldap3.core.exceptions import LDAPSocketOpenError

from oudjat.connectors.connector import Connector
from oudjat.utils import Context
from oudjat.utils.credentials import NoCredentialsError
from oudjat.utils.types import StrType

from .exceptions import (
    InvalidLDAPEntryError,
    LDAPConnectionError,
    LDAPSchemaError,
    LDAPUnreachableServerError,
)
from .ldap_filter import LDAPFilter, LDAPFilterStrFormat
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
        server: str,
        username: str | None = None,
        password: str | None = None,
        use_tls: bool = False,
    ) -> None:
        """
        Create a new LDAPConnector.

        Args:
            server (str)      : Server name
            username (str)    : Username to use for the connection
            password (str)    : Password to use for the connection
            service_name (str): Service name used to store credentials
            use_tls (bool)    : Should the connector use TLS for LDAPS connection
        """

        self._use_tls: bool = use_tls
        self._port: "LDAPPort" = LDAPPort.TLS if use_tls else LDAPPort.DEFAULT

        super().__init__(target=server, username=username, password=password)

        self.logger = logging.getLogger(__name__)
        self._domain: str = ""
        self._default_search_base: str = ""
        self._ldap_server: ldap3.Server
        self._connection: ldap3.Connection | None = None

        context = Context()
        self.logger.debug(f"{context}::New LDAPConnector - {self._target}:{self._port}")

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
        self.logger.info(f"{context}::Connecting to {self._target}")

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
                    self.logger.warning(f"{context}::Error while trying to connect to LDAP: {e}")

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

        self.logger.info(f"{context}::Bound to {ldap_server}")

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

        if payload is None:
            payload = {}

        payload["generator"] = False

        # INFO: If the search type is default : final filter is equal to provided search filter
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
        payload["attributes"] = attributes or search_type.attributes

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

    def objects(
        self,
        search_filter: "LDAPFilter | str | None" = None,
        attributes: "StrType | None" = None,
        search_base: str | None = None,
        payload: dict[str, Any] | None = None,
    ) -> list["LDAPEntry"]:
        """
        Specific method to retrieve LDAP User instances.

        Args:
            search_filter (str)            : Filter to reduce search results
            attributes (str | list[str])   : Attributes to include in result
            search_base (str)              : Where to base the search on in terms of directory location
            payload (dict[str, Any] | None): Payload to send to the server

        Returns:
            list[LDAPEntry]: A list of entries based on the provided arguments and payload
        """

        entries = self.fetch(
            search_type=LDAPObjectType.DEFAULT,
            search_base=search_base,
            search_filter=search_filter,
            attributes=attributes,
            payload=payload,
        )

        return entries

    def computers(
        self,
        search_filter: "LDAPFilter | str | None" = None,
        attributes: "StrType | None" = None,
        search_base: str | None = None,
        payload: dict[str, Any] | None = None,
    ) -> list["LDAPEntry"]:
        """
        Specific method to retrieve LDAP Computer instances.

        Args:
            search_filter (str)            : filter to reduce search results
            attributes (str | list[str])   : attributes to include in result
            search_base (str)              : where to base the search on in terms of directory location
            payload (dict[str, Any] | None): Payload to send to the server

        Returns:
            list[LDAPEntry]: A list of entries based on the provided arguments and payload
        """

        entries = self.fetch(
            search_type=LDAPObjectType.COMPUTER,
            search_base=search_base,
            search_filter=search_filter,
            attributes=attributes,
            payload=payload,
        )

        return entries

    def users(
        self,
        search_filter: "LDAPFilter | str | None" = None,
        attributes: "StrType | None" = None,
        search_base: str | None = None,
        payload: dict[str, Any] | None = None,
    ) -> list["LDAPEntry"]:
        """
        Specific method to retrieve LDAP User instances.

        Args:
            search_filter (str)            : filter to reduce search results
            attributes (str | list[str])   : attributes to include in result
            search_base (str)              : where to base the search on in terms of directory location
            payload (dict[str, Any] | None): Payload to send to the server

        Returns:
            list[LDAPEntry]: A list of entries based on the provided arguments and payload
        """

        entries = self.fetch(
            search_type=LDAPObjectType.USER,
            search_base=search_base,
            search_filter=search_filter,
            attributes=attributes,
            payload=payload,
        )

        return entries

    def groups(
        self,
        search_filter: "LDAPFilter | str | None" = None,
        search_base: str | None = None,
        attributes: "StrType | None" = None,
        payload: dict[str, Any] | None = None,
    ) -> list["LDAPEntry"]:
        """
        Specific method to retrieve LDAP group objects.

        Args:
            search_filter (str)            : Filter to reduce search results
            attributes (str | list[str])   : Attrbutes to include in result
            search_base (str)              : Where to base the search on in terms of directory location
            payload (dict[str, Any] | None): Payload to send to the server

        Returns:
            list[LDAPEntry]: A list of entries based on the provided arguments and payload
        """

        entries = self.fetch(
            search_type=LDAPObjectType.GROUP,
            search_base=search_base,
            search_filter=search_filter,
            attributes=attributes,
            payload=payload,
        )

        return entries

    def gpos(
        self,
        displayName: str = "*",
        name: StrType = "*",
        attributes: "StrType | None" = None,
        payload: dict[str, Any] | None = None,
    ) -> list["LDAPEntry"]:
        """
        Specific method to retrieve LDAP GPO instances.

        Args:
            displayName (str)              : GPO display name
            name (StrType)                 : GPO name
            attributes (str | list[str])   : Attributes to include in result
            payload (dict[str, Any] | None): Payload to send to the server

        Returns:
            list[LDAPEntry]: A list of entries based on the provided arguments and payload
        """

        name_filter = LDAPFilter()
        if isinstance(name, list):
            name_filter.set_operator_from_str("|")

            for link in name:
                name_filter.add_node(LDAPFilter(f"(name={link})"))

        else:
            name_filter = LDAPFilter(f"(name={name})")

        entries = self.fetch(
            search_type=LDAPObjectType.GPO,
            search_base=None,
            search_filter=(LDAPFilter(f"(displayName={displayName})") & name_filter),
            attributes=attributes,
            payload=payload,
        )

        return entries

    def ous(
        self,
        search_filter: "LDAPFilter | str | None" = None,
        search_base: str | None = None,
        attributes: "StrType | None" = None,
        payload: dict[str, Any] | None = None,
    ) -> list["LDAPEntry"]:
        """
        Specific method to retrieve LDAP organizational unit objects.

        Args:
            dn (str):                      : Optional distinguished name to search
            search_filter (str)            : Filter to reduce search results
            attributes (str | list[str])   : Attrbutes to include in result
            search_base (str)              : Where to base the search on in terms of directory location
            payload (dict[str, Any] | None): Payload to send to the server

        Returns:
            list[LDAPEntry]: A list of entries based on the provided arguments and payload
        """

        entries = self.fetch(
            search_type=LDAPObjectType.OU,
            search_base=search_base,
            search_filter=search_filter,
            attributes=attributes,
            payload=payload,
        )

        return entries

    def subnets(
        self,
        search_filter: "LDAPFilter | str | None" = None,
        attributes: "StrType | None" = None,
        payload: dict[str, Any] | None = None,
    ) -> list["LDAPEntry"]:
        """
        Specific method to retrieve LDAP subnet instances.

        Args:
            search_filter (str)            : Filter to reduce search results
            attributes (str | list[str])   : Attributes to include in result
            payload (dict[str, Any] | None): Payload to send to the server

        Returns:
            list[LDAPEntry]: A list of entries based on the provided arguments and payload
        """

        sb_dc = ",".join([f"DC={dc.lower()}" for dc in self.domain.split(".")])

        entries = self.fetch(
            search_type=LDAPObjectType.SUBNET,
            search_base=f"CN=Subnets,CN=Sites,CN=Configuration,{sb_dc}",
            search_filter=search_filter,
            attributes=attributes,
            payload=payload,
        )

        return entries

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

    def domain_admins(self) -> list["LDAPEntry"]:
        """
        Return a list of the domain and enterprise admins.

        Returns:
            dict[int | str, LDAPUser]: a list of LDAPEntry instances representing the domain admins
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
