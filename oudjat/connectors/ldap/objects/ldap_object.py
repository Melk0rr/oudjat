"""A generic module to describe shared behavior of more specific LDAP objects."""

import re
from datetime import datetime
from typing import TYPE_CHECKING, Any, TypeVar, override

from oudjat.utils.time_utils import DateFlag, DateFormat, TimeConverter

if TYPE_CHECKING:
    from ..ldap_connector import LDAPConnector
    from .account.group.ldap_group import LDAPGroup
    from .ldap_entry import LDAPEntry

# ****************************************************************
# Helper functions


def parse_dn(dn: str) -> dict[str, list[str]]:
    """
    Parse a DN into pieces.

    Args:
        dn (str) : distinguished name to parse

    Returns:
        Dict : dictionary of dn pieces (CN, OU, DC)
    """

    pieces: dict[str, list[str]] = {}
    for dn_part in re.split(r",(?! )", dn):
        part_type, part_value = dn_part.split("=")

        if part_type not in pieces.keys():
            pieces[part_type] = list()

        pieces[part_type].append(part_value)

    return pieces


class LDAPObject:
    """
    Defines common properties and behavior accross LDAP objects.
    """

    # ****************************************************************
    # Attributes & Constructors

    def __init__(self, ldap_entry: "LDAPEntry") -> None:
        """
        Initialize an LDAP Entry-based object.

        This method initializes the object with data from an LDAP entry.

        Args:
            ldap_entry (LDAPEntry) : ldap entry instance to be used to populate object data
        """

        self.entry: LDAPEntry = ldap_entry
        self.dn: str = self.entry.dn
        self.name: str = self.entry.get("name")
        self.uuid: str = self.entry.get("objectGUID")
        self.sid: str = self.entry.get("objectSid")
        self.description: str = self.entry.get("description", "")

        self.classes: list[str] = self.entry.get("objectClass", [])

        self.dn_pieces: dict[str, list[str]] = parse_dn(self.dn)
        self.domain: str = ".".join(self.dn_pieces.get("DC", [])).lower()

        self.creation_date: datetime = TimeConverter.str_to_date(self.entry.get("whenCreated"))
        self.change_date: datetime = TimeConverter.str_to_date(self.entry.get("whenChanged"))

        self.ldap_obj_flags: list[str] = []

    # ****************************************************************
    # Methods

    def get_dn(self) -> str:
        """
        Getter for ldap object dn.

        Returns:
            str: The distinguished name (DN) of the LDAP object.
        """

        return self.entry.dn

    def get_name(self) -> str:
        """
        Getter for ldap object name.

        Returns:
            str: The name attribute of the LDAP object.
        """

        return self.name

    def get_sid(self) -> str:
        """
        Getter for ldap object sid.

        Returns:
            str: The security identifier (SID) of the LDAP object.
        """

        return self.sid

    def get_uuid(self) -> str:
        """
        Getter for ldap object uuid.

        Returns:
            str: The universally unique identifier (UUID) of the LDAP object.
        """

        return self.uuid

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

    def get_dn_pieces(self) -> dict[str, list[str]]:
        """
        Getter for object dn pieces.

        Returns:
            dict: A dictionary containing the individual components of the DN (Distinguished Name) of the LDAP object.
        """

        return self.dn_pieces

    def get_description(self) -> str:
        """
        Getter for ldap object description.

        Returns:
            str: The description attribute of the LDAP object.
        """

        return self.description

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

        return ou_name in self.dn if recursive else f"{self.get_name()}OU={ou_name}" in self.dn

    def is_member_of(
        self, ldap_connector: "LDAPConnector", ldap_group: "LDAPGroup", extended: bool = False
    ) -> bool:
        """
        Check whether the current object is a member of the provided group.

        Args:
            ldap_connector (LDAPConnector): The LDAP connection object used to perform the membership check.
            ldap_group (LDAPGroup)        : The group to which the user's membership should be checked against.
            extended (bool, optional)     : A flag indicating whether an extended search should be performed. Defaults to False.

        Returns:
            bool: True if the current user is a member of the provided LDAP group; otherwise, False.
        """

        return ldap_connector.is_object_member_of(
            ldap_object=self, ldap_group=ldap_group, extended=extended
        )

    @override
    def __str__(self) -> str:
        """
        Convert the current instance into a string.

        Returns:
            str : string representing the LDAP object instance (basically its DN)
        """

        return self.get_dn()

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the current instance into a dictionary.

        Returns:
            dict: A dictionary containing the attributes of the LDAP object in a structured format
        """

        return {
            "dn": self.dn,
            "name": self.name,
            "guid": self.uuid,
            "sid": self.sid,
            "classes": self.classes,
            "description": self.description,
            "domain": self.domain,
            "creation_date": TimeConverter.date_to_str(
                self.creation_date, DateFormat.from_flag(DateFlag.YMD_HMS)
            ),
            "change_date": TimeConverter.date_to_str(
                self.change_date, DateFormat.from_flag(DateFlag.YMD_HMS)
            ),
            "oudjat_flags": self.ldap_obj_flags,
        }


LDAPObjectBoundType = TypeVar("LDAPObjectBoundType", bound=LDAPObject)
