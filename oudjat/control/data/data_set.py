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
        initial_set: Union[List[Dict], "DataSet"] = None,
        filters: Union[List[Dict], List["DataFilter"]] = [],
        description: str = None,
    ):
        """
        Constructor for DataSet class.

        Args:
            name (str)                                               : The name of the dataset.
            perimeter (str)                                          : The perimeter or boundary of the dataset.
            scope (Union[List[Dict], "DataSet"], optional)           : Initial data set or list of dictionaries representing data. Defaults to None.
            filters (Union[List[Dict], List["DataFilter"]], optional): Filters applied to the data. Defaults to an empty list.
            description (str, optional)                              : A brief description of the dataset. Defaults to None.
        """

        self.name = name
        self.description = description
        self.perimeter = perimeter

        self.initial_scope = initial_set

        self.filters = DataFilter.get_valid_filters_list(filters)

    # ****************************************************************
    # Methods

    def get_name(self) -> str:
        """
        Getter for the dataset name.

        Returns:
            str: The name of the dataset.
        """

        return self.name

    def get_initial_scope(self) -> Union[List[Dict], "DataSet"]:
        """
        Retrieves the initial scope dataset or a list of dictionaries that define the starting point for this dataset.

        Returns:
            Union[List[Dict], "DataSet"]: The initial scope data set or list of dictionaries.
        """

        return self.initial_scope

    def get_initial_scope_name(self) -> str:
        """
        Getter for the name of the initial scope data set.

        Returns:
            str: The name of the initial scope data set, or None if not applicable.
        """

        return self.initial_scope.get_name() if isinstance(self.initial_scope, DataSet) else None

    def get_input_data(self) -> List[Dict]:
        """
        Getter for input data.

        Returns:
            List[Dict]: The input data either from the initial scope or directly if not a DataSet.
        """

        return (
            self.initial_scope.get_data()
            if isinstance(self.initial_scope, DataSet)
            else self.initial_scope
        )

    def get_perimeter(self) -> str:
        """
        Getter for the perimeter of the dataset.

        Returns:
            str: The perimeter string.
        """

        return self.perimeter

    def set_initial_scope(self, scope: Union[List[Dict], "DataSet"]) -> None:
        """
        Setter for the initial scope data set or list of dictionaries.

        Args:
            scope (Union[List[Dict], "DataSet"]): The new initial scope to be set.
        """

        self.initial_scope = scope

    def set_filters(self, filters: Union[List[Dict], List["DataFilter"]] = []) -> None:
        """
        Setter for the list of data filters.

        Args:
            filters (Union[List[Dict], List["DataFilter"]], optional): The new list of filters to be set. Defaults to an empty list.
        """

        self.filters = DataFilter.get_valid_filters_list(filters)

    def get_data(self) -> List[Dict]:
        """
        Getter for the filtered data in the dataset's perimeter.

        Returns:
            List[Dict]: The list of dictionaries representing the filtered data.

        Raises:
            ValueError: If no parent scope is defined.
        """

        if self.initial_scope is None:
            raise ValueError(
                f"{__class__.__name__}.get_data::No parent scope defined for the current scope {self.name}"
            )

        data = self.get_input_data()

        if len(self.filters) > 0:
            data = DataFilter.filter_data(data, self.filters)

        return data

    # ****************************************************************
    # Static methods

    @staticmethod
    def get_dataset_perimeter(dataset: "DataSet") -> str:
        """
        Returns the perimeter of the provided DataSet instance

        Args:
            dataset (DataSet): DataSet instance the perimeter will be returned

        Returns:
            str: the perimeter of the provided dataset
        """

        return dataset.get_perimeter()

    @staticmethod
    def get_dataset_data(dataset: "DataSet") -> str:
        """
        Returns the data of the provided DataSet instance

        Args:
            dataset (DataSet): DataSet instance the data will be returned

        Returns:
            str: the perimeter of the provided dataset
        """

        return dataset.get_data()

    @staticmethod
    def merge_sets(name: str, sets: List["DataSet"]) -> "DataSet":
        """
        Static method to merge multiple DataSet instances into one.

        Args:
            name (str)              : The name of the merged dataset.
            scopes (List["DataSet"]): A list of DataSet instances to be merged.

        Returns:
            DataSet: A new DataSet instance containing the merged data from all provided scopes.

        Raises:
            ValueError: If the scopes do not have the same perimeter.
        """

        # Check if all scopes are on the same perimeter
        perimeters = set(map(DataSet.get_dataset_perimeter, sets))
        if len(perimeters) > 1:
            raise ValueError(
                f"{__class__.__name__}.merge_sets::Please provide scopes with the same perimeter"
            )

        return DataSet(
            name=name,
            perimeter=list(perimeters)[0],
            initial_set=list(map(DataSet.get_dataset_data, sets)),
            filters=[],
        )
