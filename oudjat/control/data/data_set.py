"""A module that describes data sets and provides tools to manipulate them."""

from typing import Any, TypeAlias

from .data_filter import DataFilter

DataSetType: TypeAlias = list[dict[str, Any]] | "DataSet"


class DataSet:
    """DataSet class : handling data unfiltered and filtered state."""

    # ****************************************************************
    # Attributes & Constructors

    def __init__(
        self,
        name: str,
        perimeter: str,
        initial_set: DataSetType | None = None,
        filters: list[dict[str, Any]] | list["DataFilter"] | None = None,
        description: str | None = None,
    ) -> None:
        """
        Create a new DataSet instance.

        Args:
            name (str)                                               : the name of the dataset.
            perimeter (str)                                          : the perimeter or boundary of the dataset.
            initial_set (Union[List[Dict], "DataSet"], optional)     : initial data set or list of dictionaries representing data. Defaults to None.
            filters (Union[List[Dict], List["DataFilter"]], optional): filters applied to the data. Defaults to an empty list.
            description (str, optional)                              : a brief description of the dataset. Defaults to None.
        """

        if filters is None:
            filters = []

        self.name: str = name
        self.description: str | None = description
        self.perimeter: str = perimeter

        self.initial_scope: DataSetType | None = initial_set

        self.filters: list[DataFilter] = DataFilter.get_valid_filters_list(filters)

    # ****************************************************************
    # Methods

    def get_name(self) -> str:
        """
        Getter for the dataset name.

        Returns:
            str: The name of the dataset.
        """

        return self.name

    def get_initial_scope(self) -> DataSetType | None:
        """
        Retrieve the initial scope dataset or a list of dictionaries that define the starting point for this dataset.

        Returns:
            Union[List[Dict], "DataSet"]: The initial scope data set or list of dictionaries.
        """

        return self.initial_scope

    def get_initial_scope_name(self) -> str | None:
        """
        Getter for the name of the initial scope data set.

        Returns:
            str: The name of the initial scope data set, or None if not applicable.
        """

        return self.initial_scope.get_name() if isinstance(self.initial_scope, DataSet) else None

    def get_input_data(self) -> list[dict[str, Any]] | None:
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

    def set_initial_scope(self, scope: DataSetType) -> None:
        """
        Setter for the initial scope data set or list of dictionaries.

        Args:
            scope (Union[List[Dict], "DataSet"]): The new initial scope to be set.
        """

        self.initial_scope = scope

    def set_filters(self, filters: list["DataFilter"]) -> None:
        """
        Setter for the list of data filters.

        Args:
            filters (Union[List[Dict], List["DataFilter"]], optional): The new list of filters to be set. Defaults to an empty list.
        """

        self.filters = DataFilter.get_valid_filters_list(filters)

    def get_data(self) -> list[dict[str, Any]]:
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
    def get_dataset_data(dataset: "DataSet") -> list[dict[str, Any]]:
        """
        Return the data of the provided DataSet instance.

        Args:
            dataset (DataSet): DataSet instance the data will be returned

        Returns:
            str: the perimeter of the provided dataset
        """

        return dataset.get_data()

    @staticmethod
    def merge_sets(name: str, sets: list["DataSet"]) -> "DataSet":
        """
        Merge multiple DataSet instances into one.

        Args:
            name (str)            : The name of the merged dataset.
            sets (List["DataSet"]): A list of DataSet instances to be merged.

        Returns:
            DataSet: A new DataSet instance containing the merged data from all provided scopes.

        Raises:
            ValueError: If the scopes do not have the same perimeter.
        """

        def map_ds_perim(dataset: "DataSet") -> str:
            return dataset.get_perimeter()

        # Check if all scopes are on the same perimeter
        perimeters = set(map(map_ds_perim, sets))
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
