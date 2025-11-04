"""
A module that facilitates the handling of LDAP filters.
"""
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

    def __init__(self, operator: str | None, *elements: "LDAPFilter | str") -> None:
        """
        Create a new instance of LDAPFilter.

        Args:
            operator (str)              : The filter join operator
            *elements (LDAPFilter | str): elements composing the filter
        """

        self._operator: "LDAPFilterOperator | None" = LDAPFilterOperator(operator)
        self._elements: list["LDAPFilter"] = []

        self._value: tuple[str, str, str] | None = None

    # ****************************************************************
    # Methods

    # ****************************************************************
    # Static methods
