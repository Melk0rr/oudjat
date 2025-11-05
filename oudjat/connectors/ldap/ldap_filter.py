"""
A module that facilitates the handling of LDAP filters.
"""

from enum import Enum
from typing import TypeAlias, override


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

        return [o.value for o in LDAPFilterOperator]


class LDAPFilterComparisonOperator(Enum):
    """
    A helper enumeration to list possible LDAP filter comparison operators.
    """

    EQ = "="
    GE = ">="
    LE = "<="
    AE = "~="

    @staticmethod
    def values() -> list[str]:
        """
        Return a list of LDAPFilterComparisonOperator values.

        Returns:
            list[str]: String values of LDAPFilterComparisonOperator
        """

        return [o.value for o in LDAPFilterComparisonOperator]


LDAPFilterParsedTupleType: TypeAlias = tuple[str, str, str] | tuple[str, list[tuple[str, str, str]]]


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

        self._filter: str = str_filter.strip()
        self._position: int = 0

    def parse(self) -> "LDAPFilterParsedTupleType":
        """
        Parse the provided filter.

        Returns:
            tuple[str, str, str] | list[tuple[str, tuple[str, str, str]]]: Parsed content
        """

        self._skip_wspace()

        if not self._filter.startswith("(") and self._filter.endswith(")"):
            raise ValueError(
                f"{__class__.__name__}._parse::Invalid LDAP filter string. Must start with '(' and end with ')'"
            )

        self._consume("(")
        res = self._parse_node()
        self._consume(")")
        self._skip_wspace()

        if self._position != len(self._filter):
            raise ValueError(f"{__class__.__name__}.parse::Unexpected trailing characters")

        return res

    def _parse_node(self) -> "LDAPFilterParsedTupleType":
        """
        Parse an LDAP filter node.

        Returns:
            LDAPFilterParsedTupleType: Parsed node as a tuple, see type alias.
        """

        operator = self._peek()
        f_nodes = []

        def parse_node() -> None:
            self._consume("(")
            f_nodes.append(self._parse_node())
            self._consume(")")

        if operator in LDAPFilterOperator.values():
            self._consume(operator)
            if operator == LDAPFilterOperator.NOT.value:
                parse_node()

            else:
                while self._peek() == "(":
                    parse_node()

            return (operator, f_nodes)

        else:
            prop = self._parse_until([v[0] for v in LDAPFilterComparisonOperator.values()])
            cmp_ope = self._parse_cmp_operator()
            value = self._parse_until([")"])

            return (prop, cmp_ope, value)

    def _parse_cmp_operator(self) -> str:
        """
        Parse a comparison operator from the current parser position.

        Returns:
            str: The comparison operator found from the current position

        Raises:
            ValueError: If no comparison operator is found
        """

        for cmp_ope in LDAPFilterComparisonOperator:
            if self._peek() == cmp_ope.value:
                self._position += len(cmp_ope.value)
                return cmp_ope.value

        raise ValueError(
            f"{__class__.__name__}._parse_cmp_operator::Invalid comparison operator found at {self._position}"
        )

    def _peek(self) -> str | None:
        """
        Return the current character at the parser position.

        Returns:
            str | None: The current character at parser position. Else None
        """

        return self._filter[self._position] if self._position < len(self._filter) else None

    def _consume(self, ch: str) -> None:
        """
        Consume the provided character if it matches the current parser position.

        Args:
            ch (str): The character to consume
        """

        if self._peek() == ch:
            self._position += 1

        else:
            raise ValueError(
                f"{__class__.__name__}._consume::Expected {ch} at position {self._position}, but found {self._peek()}"
            )

    def _parse_until(self, chars: list[str]) -> str:
        """
        Parse a substring of the provided filter until one of the provided characters is met.

        Args:
            chars (list[str]): List of stop characters

        Returns:
            str: Parsed substring
        """

        start = self._position
        while self._position < len(self._filter) and self._filter[self._position] not in chars:
            self._position += 1

        return self._filter[start : self._position].strip()

    def _skip_wspace(self) -> None:
        """
        Skip filter white space from the current parser position.
        """

        while self._position < len(self._filter) and self._filter[self._position].isspace():
            self._position += 1


class LDAPFilter:
    """
    A helper class to handle LDAP filter manipulations.
    """

    # ****************************************************************
    # Attributes & Constructor

    REG: str = r"\(([^=~<>]+)([=~<>]{1,2})([^)]+)\)"

    def __init__(
        self,
        str_filter: str | None = None,
        tuple_filter: "LDAPFilterParsedTupleType | None" = None,
        operator: str | None = None,
        *elements: "LDAPFilter",
    ) -> None:
        """
        Create a new instance of LDAPFilter.

        Args:
            str_filter (str)                        : A string representation of the filter
            tuple_filter (LDAPFilterParsedTupleType): A tuple representation of the filter
            operator (str)                          : The filter join operator
            *elements (LDAPFilter | str)            : elements composing the filter
        """

        self._operator: "LDAPFilterOperator | None" = LDAPFilterOperator(operator) if operator else None
        self._nodes: list["LDAPFilter"] = list(elements) or []

        self._value: tuple[str, str, str] | None = None

        if str_filter:
            self._parse(str_filter)

        elif tuple_filter:
            self._from_tuple(tuple_filter)

    # ****************************************************************
    # Methods
    # TODO: AND method
    # TODO: OR method
    # TODO: Add nodes method
    # TODO: Escape special chars

    @property
    def value(self) -> tuple[str, str, str] | None:
        """
        Return the value of the filter.

        Returns:
            tuple[str, str, str] | None: The tuple value if the filter is a simple node. Else None
        """

        return self._value

    @property
    def operator(self) -> "LDAPFilterOperator | None":
        """
        Return the filter operator.

        Returns:
            LDAPFilterOperator | None: The operator if the filter is composed multiple nodes. Else None
        """

        return self._operator

    @property
    def nodes(self) -> list["LDAPFilter"]:
        """
        Return the sub filter nodes of the current filter.

        Returns:
            list[LDAPFilter]: A list of the nodes composing the filter. Empty if the filter is simple
        """

        return self._nodes

    def _parse(self, str_filter: str) -> None:
        """
        Parse a string representation of an LDAPFilter.

        Args:
            str_filter: String representation of a filter
        """

        parser = LDAPFilterParser(str_filter)
        self._from_tuple(parser.parse())

    def _from_tuple(self, tuple_filter: "LDAPFilterParsedTupleType") -> None:
        """
        Use a tuple representation of an LDAP filter to populate the current instance.

        Args:
            tuple_filter (LDAPFilterParsedTupleType): Tuple representation of an LDAPFilter
        """

        if len(tuple_filter) == 3:
            self._value = tuple_filter

        elif len(tuple_filter) == 2:
            self._operator = LDAPFilterOperator(tuple_filter[0])
            self._nodes = [ LDAPFilter(tuple_filter=sub) for sub in tuple_filter[1] ]

    def add_node(self, node: "LDAPFilter") -> None:
        if self._operator is not None:
            self._nodes.append(node)

    @override
    def __str__(self) -> str:
        """
        Convert the current LDAP filter into a string.

        Returns:
            str: String representation of the current LDAP filter
        """

        filter_str = "()"
        if self._value is not None:
            filter_str = "".join(self._value)

        elif self._operator is not None and self._nodes:
            nodes_str = "".join(map(str, self._nodes))
            filter_str = f"{self._operator.value}{nodes_str}"

        return f"({filter_str})"

    # ****************************************************************
    # Static methods
