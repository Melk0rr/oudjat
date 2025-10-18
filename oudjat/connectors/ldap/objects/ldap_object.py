"""A generic module to describe shared behavior of more specific LDAP objects."""

from datetime import datetime
from typing import TYPE_CHECKING, Any, Callable, NamedTuple, TypeVar, override

from oudjat.assets.generic_identifiable import GenericIdentifiable
from oudjat.utils.time_utils import DateFlag, DateFormat, TimeConverter

from ..ldap_utils import parse_dn

if TYPE_CHECKING:
    from .ldap_entry import LDAPEntry

LDAPObjectBoundType = TypeVar("LDAPObjectBoundType", bound="LDAPObject")

class LDAPCapabilities(NamedTuple):
    """
    A helper class that handle LDAP capabilities provided by an LDAPConnector to ldap entries.

    Attributes:
        ldap_search (Callable[..., list["LDAPEntry"]])                                                                  : A function to perform an LDAP search query
        ldap_python_cls (Callable[[str], "LDAPObjTypeAlias"])                                                           : A function to retrieve a specific LDAPObject class from a string
        ldap_map_entry (Callable[["LDAPEntry", "LDAPCapabilities", type["LDAPObjectBoundType"]], "LDAPObjectBoundType"]): A function to map an entry into an LDAPObject derivated
    """

    ldap_search: Callable[..., list["LDAPEntry"]]
    ldap_python_cls: Callable[[str], type["LDAPObject"]]

class LDAPObject(GenericIdentifiable):
    """
    Defines common properties and behavior accross LDAP objects.
    """

    # ****************************************************************
    # Attributes & Constructors

    def __init__(self, ldap_entry: "LDAPEntry", capabilities: "LDAPCapabilities", **kwargs: Any) -> None:
        """
        Initialize an LDAP Entry-based object.

        This method initializes the object with data from an LDAP entry.

        Args:
            ldap_entry (LDAPEntry)         : LDAP entry instance to be used to populate object data
            capabilities (LDAPCapabilities): LDAP capabilities which provide ways for an LDAP object to interact with an LDAP server through an LDAPConnector
            kwargs (Any)                   : any further arguments
        """

        self.entry: "LDAPEntry" = ldap_entry
        super().__init__(
            gid=self.entry.id,
            name=self.entry.name,
            description=self.entry.description,
        )

        self.dn: str = self.entry.dn
        self.sid: str = self.entry.get("objectSid")

        self.classes: list[str] = self.entry.object_cls

        self.dn_pieces: dict[str, list[str]] = parse_dn(self.dn)
        self.domain: str = ".".join(self.dn_pieces.get("DC", [])).lower()

        self.creation_date: datetime = TimeConverter.str_to_date(self.entry.get("whenCreated"))
        self.change_date: datetime = TimeConverter.str_to_date(self.entry.get("whenChanged"))

        self.ldap_obj_flags: list[str] = []

        self._capabilities: LDAPCapabilities = capabilities

    # ****************************************************************
    # Methods

    def get_dn(self) -> str:
        """
        Getter for ldap object dn.

        Returns:
            str: The distinguished name (DN) of the LDAP object.
        """

        return self.entry.dn

    def get_sid(self) -> str:
        """
        Getter for ldap object sid.

        Returns:
            str: The security identifier (SID) of the LDAP object.
        """

        return self.sid

    def get_entry(self) -> dict[str, Any]:
        """
        Getter for entry attributes.

        Returns:
            dict: A dictionary containing the entry attributes from the LDAP object.
        """

        return self.entry

    def get_classes(self) -> list[str]:
        """
        Getter for object classes.

        Returns:
            list of str: The 'objectClass' attribute values from the LDAP entry dictionary.
        """

        return self.entry.get("objectClass", [])

    def get_type(self) -> str:
        """
        Get ldap object type based on objectClass attribute.

        Returns:
            str: The type of the LDAP object inferred from its 'objectClass' attributes.
        """

        return self.entry.get("type", "")


    @property
    def capabilities(self) -> "LDAPCapabilities":
        """
        Return the LDAP capabilities provided by an LDAPConnector to the current entry.

        Returns:
            LDAPCapabilities: LDAP capabilities which provide ways for an LDAP entry to interact with an LDAP server through an LDAPConnector
        """

        return self._capabilities

    def get_dn_pieces(self) -> dict[str, list[str]]:
        """
        Getter for object dn pieces.

        Returns:
            dict: A dictionary containing the individual components of the DN (Distinguished Name) of the LDAP object.
        """

        return self.dn_pieces

    def get_domain(self) -> str:
        """
        Getter for object domain.

        Returns:
            str: The domain to which the LDAP object belongs.
        """

        return self.domain

    def get_account_groups(self) -> list[str]:
        """
        Getter for the account 'memberOf' property.

        Returns:
            list of str: The groups this account is a member of, as specified in the 'memberOf' attribute.
        """

        return self.entry.get("memberOf", [])

    def get_creation_date(self) -> datetime:
        """
        Getter for ldap object creation date.

        Returns:
            str: The timestamp of when the LDAP object was created.
        """

        return self.creation_date

    def get_change_date(self) -> datetime:
        """
        Getter for ldap object change date.

        Returns:
            str: The timestamp of the last modification to the LDAP object.
        """

        return self.change_date

    def is_in_ou(self, ou_name: str, recursive: bool = True) -> bool:
        """
        Check whether the current object is contained directly or indirectly in the given OU.

        Args:
            ou_name (str)   : the LDAP OU name the object is supposed to be contained in
            recursive (bool): True to check if the object is indirectly inside the OU; False to check only a direct belonging

        Returns:
            bool: True if the object is contained in the given OU; otherwise, False.
        """

        return ou_name in self.dn if recursive else f"{self.name}OU={ou_name}" in self.dn

    @override
    def __str__(self) -> str:
        """
        Convert the current instance into a string.

        Returns:
            str : string representing the LDAP object instance (basically its DN)
        """

        return self.get_dn()

    @override
    def to_dict(self) -> dict[str, Any]:
        """
        Convert the current instance into a dictionary.

        Returns:
            dict: A dictionary containing the attributes of the LDAP object in a structured format
        """

        return {
            **super().to_dict(),
            "dn": self.dn,
            "sid": self.sid,
            "classes": self.classes,
            "domain": self.domain,
            "creation_date": TimeConverter.date_to_str(
                self.creation_date, DateFormat.from_flag(DateFlag.YMD_HMS)
            ),
            "change_date": TimeConverter.date_to_str(
                self.change_date, DateFormat.from_flag(DateFlag.YMD_HMS)
            ),
            "oudjat_flags": self.ldap_obj_flags,
        }

