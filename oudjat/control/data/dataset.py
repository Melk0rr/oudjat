"""A module that describes data sets and provides tools to manipulate them."""

from typing import Any, TypeAlias

from oudjat.control.data.decisiontree import DecisionTree, DecisionTreeDictionaryProps
from oudjat.control.data.exceptions import DataSetPerimeterError
from oudjat.core.asset import Asset
from oudjat.utils import Context

DataSetType: TypeAlias = "dict[str, Asset] | DataSet"


class DataSet:
    """DataSet class : handling data unfiltered and filtered state."""

    # ****************************************************************
    # Attributes & Constructors

    def __init__(
        self,
        name: str,
        initial_set: "DataSetType | None" = None,
        decision_tree: "DecisionTree | DecisionTreeDictionaryProps | None" = None,
        description: str | None = None,
    ) -> None:
        """
        Create a new DataSet instance.

        Args:
            name (str)                                                       : The name of the dataset.
            perimeter (str)                                                  : The perimeter or boundary of the dataset.
            initial_set (DataSetType | None)                                 : Initial data set or list of dictionaries representing data.
            decision_tree (DecisionTree | DecisionTreeDictionaryProps | None): Filters applied to the data. Defaults to an empty list.
            description (str | None)                                         : A brief description of the dataset. Defaults to None.
        """

        self._name: str = name
        self._description: str | None = description

        self._initial_set: "DataSetType" = initial_set if initial_set is not None else {}

        self._perimeter: type["Asset"] = next(iter(self.initial_set_data.values())).__class__

        types = set([asset.__class__.__name__ for asset in self.initial_set_data.values()])
        if len(types) > 1:
            raise DataSetPerimeterError(f"{Context()}::Please provide data with same asset types")

        if decision_tree is not None and not isinstance(decision_tree, DecisionTree):
            decision_tree = DecisionTree(tree_dict=decision_tree)

        self._decision_tree: "DecisionTree | None" = decision_tree

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
    def perimeter(self) -> type["Asset"]:
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
    def decision_tree(self) -> "DecisionTree | None":
        """
        Return the data filters associated to this DataSet.

        Returns:
            DecisionTree | None: DecisionTree that determines the data set output
        """

        return self._decision_tree

    @decision_tree.setter
    def decision_treinitial_set_datae(self, new_decision_tree: "DecisionTree") -> None:
        """
        Setter for the list of data filters.

        Args:
            new_decision_tree (DecisionTree): New decision tree value
        """

        self._decision_tree = new_decision_tree

    @property
    def initial_set_data(self) -> dict[str, "Asset"]:
        """
        Getter for input data.

        Returns:
            dict[str, Asset]: The input data either retrieved through initial DataSet.output_data or the initial_set directly
        """

        return (
            self._initial_set.output_data
            if isinstance(self._initial_set, DataSet)
            else self._initial_set
        )

    @property
    def _is_initial_set_empty(self) -> bool:
        """
        Check if input data is null or empty.

        Returns:
            bool: True if input data is null or empty. False otherwise
        """

        return len(self.initial_set_data) == 0

    @property
    def output_data(self) -> dict[str, "Asset"]:
        """
        Getter for the filtered data in the dataset's perimeter.

        Returns:
            list[dict[str, Any]]: The list of dictionaries representing the filtered data.
        """

        data = self.initial_set_data
        if not self._is_initial_set_empty and self._decision_tree is not None:
            data = {k: v for k, v in data.items() if self._decision_tree.value(v.to_dict())}

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
            "decisionTree": self._decision_tree.to_dict() if self._decision_tree else {},
            "initialSet": {"name": self.initial_set_name, "size": len(self.initial_set_data)},
            "outputDataSize": len(self.output_data),
        }

    # ****************************************************************
    # Class methods

    @classmethod
    def merge_sets(cls, name: str, sets: list["DataSet"]) -> "DataSet":
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

        def dataset_data(dataset: "DataSet") -> dict[str, "Asset"]:
            return dataset.output_data

        # Check if all sets are on the same perimeter
        if len(set([ds.perimeter for ds in sets])) > 1:
            raise DataSetPerimeterError(
                f"{Context()}::Please provide data sets with the same perimeter"
            )

        initial_set = {}
        for dataset in map(dataset_data, sets):
            initial_set.update(dataset)

        return cls(
            name=name,
            initial_set=initial_set,
        )
