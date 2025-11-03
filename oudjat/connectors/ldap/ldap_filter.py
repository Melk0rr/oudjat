# TODO: Implement

from enum import Enum


class LDAPFilterOperator(Enum):
    """
    A helper enumeration to list possible LDAP filter join operators.
    """

    AND = "&"
    OR = "|"
    NOT = "!"


class LDAPFilterComparisonOperator(Enum):
    """
    A helper enumeration to list possible LDAP filter comparison operators.
    """

    EQ = "="
    GE = ">="
    LE = "<="
    AE = "~="


class LDAPFilter:
    """
    A helper class to handle LDAP filter manipulations.
    """

    # ****************************************************************
    # Attributes & Constructor

    REG: str = r"\(([^=~<>]+)([=~<>]{1,2})([^)]+)\)"
    # ****************************************************************
    # Methods

    # ****************************************************************
    # Static methods
