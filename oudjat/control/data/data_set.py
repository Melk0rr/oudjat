from typing import Dict, List, Union

from .data_filter import DataFilter


class DataSet:
    """DataSet class : handling data unfiltered and filtered state"""

    # ****************************************************************
    # Attributes & Constructors

    def __init__(
        self,
        name: str,
        perimeter: str,
        scope: Union[List[Dict], "DataSet"] = None,
        filters: Union[List[Dict], List["DataFilter"]] = [],
        description: str = None,
    ):
        """Constructor"""

        self.name = name
        self.description = description
        self.perimeter = perimeter

        self.initial_scope = scope

        self.filters = DataFilter.get_valid_filters_list(filters)

    # ****************************************************************
    # Methods

    def get_name(self) -> str:
        """Getter for perimeter name"""

        return self.name

    def get_initial_scope(self) -> Union[List[Dict], "DataSet"]:
        """Getter for parent scope"""

        return self.initial_scope

    def get_initial_scope_name(self) -> str:
        """Getter for initial scope name"""

        return self.initial_scope.get_name() if isinstance(self.initial_scope, DataSet) else None

    def get_input_data(self) -> List[Dict]:
        """Getter for input data"""

        return (
            self.initial_scope.get_data()
            if isinstance(self.initial_scope, DataSet)
            else self.initial_scope
        )

    def get_perimeter(self) -> str:
        """Getter for perimeter"""

        return self.perimeter

    def set_initial_scope(self, scope: Union[List[Dict], "DataSet"]) -> None:
        """Setter for input data"""

        self.initial_scope = scope

    def set_filters(self, filters: Union[List[Dict], List["DataFilter"]] = []) -> None:
        """Setter for filters"""

        self.filters = DataFilter.get_valid_filters_list(filters)

    def get_data(self) -> List[Dict]:
        """Getter for perimeter data"""

        if self.initial_scope is None:
            raise ValueError(
                f"{__class__}: no parent scope defined for the current scope {self.name}"
            )

        data = self.get_input_data()

        if len(self.filters) > 0:
            data = DataFilter.filter_data(data, self.filters)

        return data

    # ****************************************************************
    # Static methods

    @staticmethod
    def merge_sets(name: str, scopes: List["DataSet"]) -> "DataSet":
        """Merges given scopes into one"""

        # Check if all scopes are on the same perimeter
        perimeters = set([s.get_perimeter() for s in scopes])
        if len(perimeters) > 1:
            raise ValueError(
                f"{__class__}: Error merging scopes. Please provide scopes with the same perimeter"
            )

        merge_data = []
        for s in scopes:
            merge_data.extend(s.get_data())

        merge = DataSet(name=name, perimeter=list(perimeters)[0], scope=merge_data, filters=[])

        return merge

