"""A module that describes data sets and provides tools to manipulate them."""

from typing import Any, TypeAlias

from oudjat.control.data.exceptions import DataSetPerimeterError
from oudjat.utils import Context, DataType

from .data_filter import DataFilter, DataFilterDictionaryProps

DataSetType: TypeAlias = "DataType | DataSet"


class DataSet:
    """DataSet class : handling data unfiltered and filtered state."""

    # ****************************************************************
    # Attributes & Constructors

    def __init__(
        self,
        name: str,
        perimeter: str,
        initial_set: "DataSetType | None" = None,
        filters: list["DataFilterDictionaryProps"] | list["DataFilter"] | None = None,
        description: str | None = None,
    ) -> None:
        """
        Create a new DataSet instance.

        Args:
            name (str)                                                  : The name of the dataset.
            perimeter (str)                                             : The perimeter or boundary of the dataset.
            initial_set (DataSetType | None)                            : Initial data set or list of dictionaries representing data. Defaults to None.
            filters (list[DataFilterDictionaryProps] | list[DataFilter]): Filters applied to the data. Defaults to an empty list.
            description (str | None)                                    : A brief description of the dataset. Defaults to None.
        """

        if filters is None:
            filters = []

        self._name: str = name
        self._description: str | None = description
        self._perimeter: str = perimeter

        self._initial_set: "DataSetType" = initial_set if initial_set is not None else []

        # TODO: Use DecisionTree instead
        self._filters: list["DataFilter"] = DataFilter.valid_filters_list(filters)

    # ****************************************************************
    # Methods

    @property
    def name(self) -> str:
        """
        Return the current DataSet name.

        Returns:
            str: The name of the dataset.
        """

        return self._name

    @property
    def initial_set(self) -> "DataSetType | None":
        """
        Retrieve the initial dataset or a list of dictionaries that define the starting point for this dataset.

        Returns:
            DataSetType: the initial data set data set or list of dictionaries.
        """

        return self._initial_set

    @initial_set.setter
    def initial_set(self, dataset: "DataSetType") -> None:
        """
        Setter for the initial data set.

        Args:
            dataset (DataSet): the new initial data set
        """

        self._initial_set = dataset

    @property
    def description(self) -> str | None:
        """
        Return the description for this DataSet.

        Returns:
            str | None: a string that describe this data set. None if no description provided.
        """

        return self._description

    @property
    def perimeter(self) -> str:
        """
        Return the current DataSet perimeter.

        Returns:
            str: The perimeter string.
        """

        return self._perimeter

    @property
    def initial_set_name(self) -> str | None:
        """
        Return the name of the initial data set.

        Returns:
            str | None: the name of the initial data set, or None if not applicable.
        """

        return self._initial_set.name if isinstance(self._initial_set, DataSet) else None

    @property
    def filters(self) -> list["DataFilter"]:
        """
        Return the data filters associated to this DataSet.

        Returns:
            list[DataFilter]: list of data filters that will determine the data set output
        """

        return self._filters

    @filters.setter
    def filters(self, filters: list["DataFilter"]) -> None:
        """
        Setter for the list of data filters.

        Args:
            filters (list[DataFilter]): The new list of filters to be set. Defaults to an empty list.
        """

        self._filters = DataFilter.valid_filters_list(filters)

    @property
    def initial_set_data(self) -> list[dict[str, Any]]:
        """
        Getter for input data.

        Returns:
            list[dict[str, Any]]: The input data either retrieved through initial DataSet.output_data or the initial_set directly
        """

        return (
            self._initial_set.output_data
            if isinstance(self._initial_set, DataSet)
            else self._initial_set
        )

    @property
    def empty_initial_set_data(self) -> bool:
        """
        Check if input data is null or empty.

        Returns:
            bool: True if input data is null or empty. False otherwise
        """

        return len(self.initial_set_data) == 0

    @property
    def output_data(self) -> list[dict[str, Any]]:
        """
        Getter for the filtered data in the dataset's perimeter.

        Returns:
            list[dict[str, Any]]: The list of dictionaries representing the filtered data.
        """

        data = self.initial_set_data
        if not self.empty_initial_set_data and len(self._filters) > 0:
            data = DataFilter.filter_data(data, self._filters)

        return data

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the current instance into a dictionary.

        Returns:
            dict[str, Any]: dictionary representation of the current instance.
        """

        return {
            "name": self.name,
            "description": self.description,
            "perimeter": self.perimeter,
            "filters": list(map(str, self.filters)),
            "initialSet": {
                "name": self.initial_set_name,
                "size": len(self.initial_set_data)
            },
            "outputDataSize": len(self.output_data),
        }

    # ****************************************************************
    # Static methods


    @staticmethod
    def merge_sets(name: str, sets: list["DataSet"]) -> "DataSet":
        """
        Merge multiple DataSet instances into one.

        Args:
            name (str)          : the name of the merged dataset.
            sets (list[DataSet]): a list of DataSet instances to be merged.

        Returns:
            DataSet: a new DataSet instance containing the merged data from all provided data sets.

        Raises:
            ValueError: if the data sets do not have the same perimeter.
        """

        def dataset_data(dataset: "DataSet") -> list[dict[str, Any]]:
            return dataset.output_data

        # Check if all sets are on the same perimeter
        perimeters = set([ds.perimeter for ds in sets])
        if len(perimeters) > 1:
            raise DataSetPerimeterError(
                f"{Context()}::Please provide data sets with the same perimeter"
            )

        return DataSet(
            name=name,
            perimeter=list(perimeters)[0],
            initial_set=[item for set_data in map(dataset_data, sets) for item in set_data],
            filters=[],
        )
