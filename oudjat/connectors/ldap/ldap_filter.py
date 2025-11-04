"""
A module that facilitates the handling of LDAP filters.
"""
# TODO: Implement

import re
from enum import Enum


class LDAPFilterOperator(Enum):
    """
    A helper enumeration to list possible LDAP filter join operators.
    """

    AND = "&"
    OR = "|"
    NOT = "!"

    @staticmethod
    def values() -> list[str]:
        """
        Return a list of LDAPFilterOperator values.

        Returns:
            list[str]: String values of LDAPFilterOperator
        """

        return [ o.value for o in LDAPFilterOperator ]


class LDAPFilterComparisonOperator(Enum):
    """
    A helper enumeration to list possible LDAP filter comparison operators.
    """

    EQ = "="
    GE = ">="
    LE = "<="
    AE = "~="


class LDAPFilterParser:
    """
    A class to parse an LDAP filter.
    """

    # ****************************************************************
    # Attributes & Constructor

    def __init__(self, str_filter: str) -> None:
        """
        Create a new LDAP filter parser.

        Args:
            str_filter (str): LDAP filter string to parse
        """

        self._filter: str = str_filter
        self._position: int = 0


class LDAPFilter:
    """
    A helper class to handle LDAP filter manipulations.
    """

    # ****************************************************************
    # Attributes & Constructor

    REG: str = r"\(([^=~<>]+)([=~<>]{1,2})([^)]+)\)"

    def __init__(self, str_filter: str | None, operator: str | None, *elements: "LDAPFilter") -> None:
        """
        Create a new instance of LDAPFilter.

        Args:
            operator (str)              : The filter join operator
            *elements (LDAPFilter | str): elements composing the filter
        """

        self._operator: "LDAPFilterOperator | None" = LDAPFilterOperator(operator)
        self._elements: list["LDAPFilter"] = list(elements) or []

        self._value: tuple[str, str, str] | None = None

        if str_filter:
            self._parse(str_filter)

    # ****************************************************************
    # Methods

    def _parse(self, str_filter: str) -> None:
        str_filter = str_filter.strip()

        if not str_filter.startswith("(") and str_filter.endswith(")"):
            raise ValueError(
                f"{__class__.__name__}._parse::Invalid LDAP filter string. Must start with '(' and end with ')'"
            )

        filter_body = str_filter[1:-1].strip()

        # Check for operator
        if filter_body and filter_body[0] in LDAPFilterOperator.values():
            self._operator = LDAPFilterOperator(filter_body[0])
            sub_filters = filter_body[1:]

        else:
            filter_match = re.match(LDAPFilter.REG, filter_body)
            if filter_match:
                self._value = (filter_match.group(1), filter_match.group(3), filter_match.group(3))

            else:
                raise ValueError(f"{__class__.__name__}._parse::Invalid LDAP filter. Simple filter does not match the expected format")

    # ****************************************************************
    # Static methods
