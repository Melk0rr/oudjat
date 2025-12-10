"""A generic module to describe shared behavior of more specific LDAP objects."""

from datetime import datetime
from typing import TYPE_CHECKING, Any, Callable, Generic, NamedTuple, TypeVar, override

from oudjat.core.generic_identifiable import GenericIdentifiable
from oudjat.utils.time_utils import DateFlag, DateFormat, TimeConverter

from ..ldap_utils import parse_dn

if TYPE_CHECKING:
    from .ldap_entry import LDAPEntry
    from .ldap_object_types import LDAPObjectType

LDAPObjectBoundType = TypeVar("LDAPObjectBoundType", bound="LDAPObject")


class LDAPObjectOptions(NamedTuple, Generic[LDAPObjectBoundType]):
    """
    Helper class to handle passing of LDAPObject derivated and dedicated method to retrive this specific type of LDAPObject.

    Attributes:
        cls (type[LDAPObject])                            : Type class of the LDAPObject derivated
        fetch (Callable[..., dict[int | str, LDAPObject]]): A function to retrieve the specific type

    """

    cls: type[LDAPObjectBoundType]
    fetch: Callable[..., list["LDAPEntry"]]


class LDAPCapabilities(NamedTuple):
    """
    A helper class that handle LDAP capabilities provided by an LDAPConnector to ldap entries.

    Attributes:
        ldap_search (Callable[..., list["LDAPEntry"]])     : A function to perform an LDAP search query
        ldap_obj_opt (Callable[[str], "LDAPObjectOptions"]): A function to retrieve a specific LDAPObjectOptions element
    """

    ldap_search: Callable[..., list["LDAPEntry"]]
    ldap_obj_opt: Callable[["LDAPObjectType"], "LDAPObjectOptions"]


class LDAPObject(GenericIdentifiable):
    """
    Defines common properties and behavior accross LDAP objects.
    """

    # ****************************************************************
    # Attributes & Constructors

    def __init__(
        self, ldap_entry: "LDAPEntry", capabilities: "LDAPCapabilities", **kwargs: Any
    ) -> None:
        """
        Initialize an LDAP Entry-based object.

        This method initializes the object with data from an LDAP entry.

        Args:
            ldap_entry (LDAPEntry)         : LDAP entry instance to be used to populate object data
            capabilities (LDAPCapabilities): LDAP capabilities providing ways for an LDAP object to interact with an LDAP server through an LDAPConnector
            kwargs (Any)                   : Any further arguments
        """

        self._entry: "LDAPEntry" = ldap_entry
        super().__init__(
            gid=self.entry.id,
            name=self.entry.name,
            description=self.entry.description,
        )

        self._ldap_obj_flags: set[str] = set()
        self._capabilities: "LDAPCapabilities" = capabilities

    # ****************************************************************
    # Methods

    @property
    def dn(self) -> str:
        """
        Getter for ldap object dn.

        Returns:
            str: The distinguished name (DN) of the LDAP object.
        """

        return self.entry.dn

    @property
    def sid(self) -> str:
        """
        Getter for ldap object sid.

        Returns:
            str: The security identifier (SID) of the LDAP object.
        """

        return self.entry.get("objectSid")

    @property
    def entry(self) -> "LDAPEntry":
        """
        Getter for entry attributes.

        Returns:
            dict: A dictionary containing the entry attributes from the LDAP object.
        """

        return self._entry

    @property
    def classes(self) -> list[str]:
        """
        Getter for object classes.

        Returns:
            list of str: The 'objectClass' attribute values from the LDAP entry dictionary.
        """

        return self.entry.object_cls

    @property
    def capabilities(self) -> "LDAPCapabilities":
        """
        Return the LDAP capabilities provided by an LDAPConnector to the current entry.

        Returns:
            LDAPCapabilities: LDAP capabilities which provide ways for an LDAP entry to interact with an LDAP server through an LDAPConnector
        """

        return self._capabilities

    @property
    def dn_pieces(self) -> dict[str, list[str]]:
        """
        Getter for object dn pieces.

        Returns:
            dict[str, list[str]]: A dictionary containing the individual components of the DN (Distinguished Name) of the LDAP object.
        """

        return parse_dn(self.dn)

    @property
    def domain(self) -> str:
        """
        Return the domain name of the current object.

        Returns:
            str: The domain to which the LDAP object belongs.
        """

        return ".".join(self.dn_pieces.get("DC", [])).lower()

    @property
    def membership(self) -> list[str]:
        """
        Return a list of LDAP groups the object is member of.

        Returns:
            list[str]: The groups this account is a member of, as specified in the 'memberOf' attribute.
        """

        return self.entry.get("memberOf", [])

    @property
    def creation_date(self) -> datetime | None:
        """
        Getter for ldap object creation date.

        Returns:
            str: The timestamp of when the LDAP object was created.
        """

        attr_value = self.entry.get("whenCreated")
        if attr_value is None:
            return attr_value

        return attr_value if isinstance(attr_value, datetime) else TimeConverter.str_to_date(attr_value)

    @property
    def change_date(self) -> datetime | None:
        """
        Getter for ldap object change date.

        Returns:
            str: The timestamp of the last modification to the LDAP object.
        """

        attr_value = self.entry.get("whenChanged")
        if attr_value is None:
            return attr_value

        return attr_value if isinstance(attr_value, datetime) else TimeConverter.str_to_date(attr_value)

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

        return self.dn

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
            "creationDate": LDAPObject._format_acc_date_str(self.creation_date),
            "changedDate": LDAPObject._format_acc_date_str(self.change_date),
            "ldapObjFlags": list(self._ldap_obj_flags),
        }

    # ****************************************************************
    # Static methods

    @staticmethod
    def _format_acc_date_str(date: datetime | None) -> str | None:
        """
        Convert an account date into a readable string.

        Args:
            date (datetime): date to convert into a readable string

        Returns:
            str: readable formated string
        """

        if date is None:
            return None

        return TimeConverter.date_to_str(date, date_format=DateFormat.from_flag(DateFlag.YMD_HMS))
