from typing import TYPE_CHECKING, Dict, List

from oudjat.utils import DATE_TIME_FLAGS, date_format_from_flag

if TYPE_CHECKING:
    from ..ldap_connector import LDAPConnector
    from .account.group.ldap_group import LDAPGroup
    from .ldap_entry import LDAPEntry


# ****************************************************************
# Helper functions


def parse_dn(dn: str) -> Dict:
    """
    Parses a DN into pieces

    Args:
        dn (str) : distinguished name to parse

    Return:
        Dict : dictionary of dn pieces (CN, OU, DN)
    """
    split = dn.split(",")
    pieces = {}

    for p in split:
        p_split = p.split("=")

        if p_split[0] not in pieces.keys():
            pieces[p_split[0]] = []

        pieces[p_split[0]].append(p_split[1])

    return pieces


class LDAPObject:
    """Generic LDAP object"""

    # ****************************************************************
    # Attributes & Constructors
    def __init__(self, ldap_entry: "LDAPEntry") -> None:
        """
        Constructor

        Args:
            ldap_entry (LDAPEntry) : ldap entry instance to be used to populate object data
        """

        self.entry = ldap_entry
        self.dn = self.entry.get_dn()
        self.name = self.entry.get("name")
        self.uuid = self.entry.get("objectGUID")
        self.sid = self.entry.get("objectSid")
        self.description = self.entry.get("description", [])

        self.classes = self.entry.get("objectClass", [])

        self.dn_pieces = parse_dn(self.dn)
        self.domain = ".".join(self.dn_pieces.get("DC")).lower()

        self.creation_date = self.entry.get("whenCreated")
        self.change_date = self.entry.get("whenChanged")

        self.oudjat_flags: List[str] = []

    # ****************************************************************
    # Methods

    def get_dn(self) -> str:
        """
        Getter for ldap object dn.

        Returns:
            str: The distinguished name (DN) of the LDAP object.
        """
        return self.dn

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

    def get_entry(self) -> Dict:
        """
        Getter for entry attributes.

        Returns:
            dict: A dictionary containing the entry attributes from the LDAP object.
        """
        return self.entry

    def get_classes(self) -> List[str]:
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

    def get_dn_pieces(self) -> Dict:
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

    def get_account_groups(self) -> List[str]:
        """
        Getter for the account 'memberOf' property.

        Returns:
            list of str: The groups this account is a member of, as specified in the 'memberOf' attribute.
        """
        return self.entry.get("memberOf", [])

    def get_creation_date(self) -> str:
        """
        Getter for ldap object creation date.

        Returns:
            str: The timestamp of when the LDAP object was created.
        """
        return self.creation_date

    def get_change_date(self) -> str:
        """
        Getter for ldap object change date.

        Returns:
            str: The timestamp of the last modification to the LDAP object.
        """
        return self.change_date

    def is_member_of(
        self, ldap_connector: "LDAPConnector", ldap_group: "LDAPGroup", extended: bool = False
    ) -> bool:
        """
        Checks whether the current user is a member of the provided group.

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

    def to_dict(self) -> Dict:
        """
        Converts the current instance into a dictionary.

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
            "creation_date": self.creation_date.strftime(date_format_from_flag(DATE_TIME_FLAGS)),
            "change_date": self.change_date.strftime(date_format_from_flag(DATE_TIME_FLAGS)),
            "oudjat_flags": self.oudjat_flags,
        }
