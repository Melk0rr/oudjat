"""A module to handle data filters."""

from typing import Any, Callable, TypeAlias, TypedDict, override

from oudjat.utils import DataType
from oudjat.utils.operators import CompareOperator
from oudjat.utils.types import FilterTupleExtType, NumberType

DataFilterDictionaryValueType: TypeAlias = NumberType | bool | str | None


class DataFilterDictionaryProps(TypedDict):
    """
    A helper class to properly handle property types of dictionaries used for data filter convertion.

    Attributes:
        fieldname (str)                      : fieldname checked for the input element that will be filtered
        operator (str)                       : name of the operator used in the filter
        value (DataFilterDictionaryValueType): value compared with the input element's field using the provided operator
    """

    fieldname: str
    operator: str | None
    value: "DataFilterDictionaryValueType"


class DataFilter:
    """
    A class to handle data filtering operations.

    Once created, a filter can be run against one or multiple elements to check if they are as expected.

    Exemple 1:
        my_filter = DataFilter(fieldname="anything", operator="=", value=9)
        check = my_filter.filter_value(8)
        print(check) -> False

    Exemple 2:
        my_filter = DataFilter(fieldname="name", operator="in", value="Batty")
        replicant = { "name": "Roy Batty", "age": 4 }
        check = my_filter.filter_dict(replicant)
        print(check) -> True
    """

    # ****************************************************************
    # Attributes & Constructors

    def __init__(
        self, fieldname: str, value: Any, operator: str = "in", negate: bool = False
    ) -> None:
        """
        Return a new instance of data filter.

        Args:
            fieldname (str): name of the field to filter
            value (Any)    : the value of the filter and the value the filtered element must have
            operator (str) : the operator used to filter the element
            negate (bool)  : if you want to negate the filter result or not (True -> False; False -> True)
        """

        if operator not in CompareOperator.list_all_keys():
            raise ValueError(f"{__class__.__name__}::Invalid operator provided: {operator}")

        self._fieldname: str = fieldname
        self._operator: "CompareOperator" = CompareOperator.find_by_key(operator)
        self._value: Any = value
        self._negate: bool = negate

    # ****************************************************************
    # Methods

    @property
    def fieldname(self) -> str:
        """
        Return the filter fieldname.

        Returns:
            str: fieldname of the instance that will be used to filter a dictionary
        """

        return self._fieldname

    @property
    def operator(self) -> "CompareOperator":
        """
        Return the filter operator.

        Returns
            str: operator used to determine which function will be used to filter
        """

        return self._operator

    @property
    def operation(self) -> Callable:
        """
        Return a DataFilterOperation based on current parameters.

        Returns:
            Callable: DataFilterOperation function
        """

        return self._operator.operation

    @property
    def value(self) -> Any:
        """
        Return the filter value.

        Returns:
            Any: the value the filtered element must have
        """
        return self._value

    @property
    def negate(self) -> bool:
        """
        Return the current data filter negation value.

        The negation value is used to 'negate' the data filter value.
        Meaning, whatever value the filter will return, it will be negated / reversed

        Returns:
            bool: True if the data filter value will be negated. False otherwise.
        """

        return self._negate

    @negate.setter
    def negate(self, new_negate_value: bool) -> None:
        """
        Set a new value for the negate attribute.

        Args:
            new_negate_value (bool): new value of the negate attribute
        """

        self._negate = new_negate_value

    def filter_dict(self, element: dict[str, Any]) -> bool:
        """
        Run the current filter against a dictionary.

        Args:
            element (Dict): element to run the filter against

        Returns:
            bool: wheither or not the dictionary matches the filter
        """

        check: bool = self.operation(element[self.fieldname], self.value)
        return not check if self.negate else check

    def filter_value(self, value: Any) -> bool:
        """
        Run the current filter against the provided value.

        Args:
            value (Any): value to run the filter against

        Returns:
            bool: wheither or not the given value matches the filter
        """

        check: bool = self.operation(value, self.value)
        return not check if self.negate else check

    @override
    def __str__(self) -> str:
        """
        Convert the current instance into a string.

        Returns:
            str: current filter converted into a string

        Exemple:
            my_filter = DataFilter(fieldname="name", operator="=", value="Roy Batty")
            print(my_filter) -> name = Roy Batty
        """

        return f"{self._fieldname} {self._operator} {self._value}"

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the current instance into a dictionary.

        Returns:
            dict[str, Any]: dictionary representation of the current data filter
        """

        return {
            "fieldname": self._fieldname,
            "operator": self._operator.name,
            "value": self._value,
            "negate": self._negate,
        }

    # ****************************************************************
    # Static methods

    @staticmethod
    def from_dict(filter_dict: "DataFilterDictionaryProps") -> "DataFilter":
        """
        Create a datafilter instance from a dictionary.

        Args:
            filter_dict (Dict): dictionary used to create DataFilter instance

        Returns:
            DataFilter: new instance

        Exemple:
            my_filter = DataFilter.from_dict({ "fieldname": "name", "operator": "=", "value": "Rick Deckard"})
        """

        return DataFilter(
            fieldname=filter_dict["fieldname"],
            operator=filter_dict.get("operator", None) or "is",
            value=filter_dict.get("value", None),
        )

    @staticmethod
    def from_tuple(filter_tuple: tuple[str, str, "DataFilterDictionaryValueType"]) -> "DataFilter":
        """
        Create a datafilter instance from a tuple.

        Args:
            filter_tuple (Tuple): tuple used to create DataFilter instance

        Returns:
            DataFilter: new instance

        Exemple:
            my_filter = DataFilter.from_tuple(( "name", "=", "Rick Deckard" ))
        """

        return DataFilter(
            fieldname=filter_tuple[0],
            operator=filter_tuple[1],
            value=filter_tuple[2],
        )

    @staticmethod
    def get_valid_filters_list(
        filters_list: list["DataFilterDictionaryProps"] | list["DataFilter"],
    ) -> list["DataFilter"]:
        """
        Check filters type and format them into DataFilter instances if needed.

        Args:
            filters_list (list[Dict] | list[DataFilter]): filter list to check / format

        Returns:
            list[DataFilter]: formated list of data filter instances
        """

        return [f if isinstance(f, DataFilter) else DataFilter.from_dict(f) for f in filters_list]

    @staticmethod
    def gen_from_dict(filters: list["DataFilterDictionaryProps"]) -> list["DataFilter"]:
        """
        Generate multiple DataFitler instances based on dictionnaries.

        Args:
            filters (List[Dict]): list of dictionaries used to generated instances

        Returns:
            List[DataFilter]: data filter instances
        """

        return list(map(DataFilter.from_dict, filters))

    @staticmethod
    def gen_from_tuple(filters: "FilterTupleExtType") -> list["DataFilter"]:
        """
        Generate DataFitler instances based on tuples.

        Args:
            filters (List[Tuple]): list of tuples used to generated instances

        Returns:
            List[DataFilter]: data filter instances
        """

        if not isinstance(filters, list):
            filters = [filters]

        return list(map(DataFilter.from_tuple, filters))

    @staticmethod
    def get_conditions(element: Any, filters: list["DataFilter"] | list["DataFilterDictionaryProps"]) -> bool:
        """
        Run all given filters against a single provided element.

        Args:
            element (Any)                          : element to check
            filters (List[Dict] | List[DataFilter]): filters to run

        Returns:
            bool: filter results
        """

        checks = []

        for f in filters:
            datafilter = f if isinstance(f, DataFilter) else DataFilter.from_dict(f)
            checks.append(datafilter.filter_dict(element))

        return all(checks)

    @staticmethod
    def filter_data(
        data_to_filter: "DataType",
        filters: "DataFilter | list[DataFilter] | None" = None,
    ) -> "DataType":
        """
        Filter data based on given filters.

        Args:
            data_to_filter (DataType)              : Well...The data to be filtered duh
            filters (DataFilter | List[DataFilter]): Filters to run

        Returns:
            DataType: Filtered data
        """

        if filters is None:
            return data_to_filter

        if not isinstance(filters, list):
            filters = [filters]

        return list(filter(lambda el: all(f.filter_dict(el) for f in filters), data_to_filter))
