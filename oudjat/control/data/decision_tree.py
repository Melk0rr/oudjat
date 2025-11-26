"""A module that provide a way to dynamically change behaviors or add properties to an object through decision trees."""

import logging
from typing import Any, TypeAlias, TypedDict, override

from oudjat.utils import Context, LogicalOperator
from oudjat.utils.list_utils import UtilsList
from oudjat.utils.mappers import any_to_dict
from oudjat.utils.types import NumberType

from .data_filter import DataFilter, DataFilterDictionaryProps
from .exceptions import DecisionTreeBuildError, DecisionTreeInvalidNodeError

DecisionNodeFlagType: TypeAlias = "NumberType | str | None"


class DecisionTreeDictionaryProps(TypedDict):
    """
    A helper class to properly handle property types of dictionaries used to generate DecisionTree instances.

    Detailed description.

    Attributes:
        operator (str)                                                       : the name of the operator used to join the tree nodes values
        nodes (list[DecisionTreeDictionaryProps | DataFilterDictionaryProps]): sub decision trees or filters that compose the tree
        negate (bool | None)                                                 : wheither or not to negate the final tree value
    """

    operator: str
    nodes: list["DecisionTreeDictionaryProps | DataFilterDictionaryProps"]
    negate: bool | None


class DecisionTreeNode:
    """
    A class that describes the behavior of a DecisionTree node.

    A DecisionTree node is essentially composed of a data filter.
    It also keeps a value computed for a particular element based on the node data filter result for that particular element.
    It can also be affected a flag that will be valid if the node value is true.
    You can then get a list of flags for the input element in the final result of the tree.
    """

    # ****************************************************************
    # Attributes & Constructors

    def __init__(self, node_dict: "DataFilterDictionaryProps") -> None:
        """
        Create a new DecisionTree node.

        Args:
            node_dict (dict[str, Any]): A dictionary containing the initialization data for the node.

        Attributes:
            flag (DecisionNodeFlagType): flag associated with this node in case the result value is true
            node_filter (DataFilter)   : data filter of this node that will be used to compute node value for a particular input element
            value (bool)               : the current value of the node for a given element
        """

        self._flag: "DecisionNodeFlagType" = node_dict.get("flag", None)
        self._node_filter: "DataFilter" = DataFilter.from_dict(node_dict)
        self._node_filter.negate = node_dict.get("negate", False)
        self._value: bool | None = None

    # ****************************************************************
    # Methods

    @property
    def flag(self) -> "DecisionNodeFlagType":
        """
        Return node flag.

        Returns:
            DecisionNodeFlagType: The flag of the node.
        """

        return self._flag

    @property
    def node_filter(self) -> "DataFilter":
        """
        Return the current node filter.

        Returns:
            DataFilter: The filter associated with the node.
        """

        return self._node_filter

    @property
    def value(self) -> bool | None:
        """
        Return the node value.

        Returns:
            bool | None: True if the compared element passed the filter. False otherwise. And None if no element was passed yet.
        """

        return self._value

    def compute_value(self, element: dict[str, Any] | None = None) -> bool:
        """
        Return the node value after init if value is not set.

        Args:
            element (dict[str, Any] | None): an element to be filtered represented as a dictionary. Defaults to None.

        Returns:
            bool: The value of the node after applying its filter if necessary.
        """

        if element:
            self.init(element)

        if self._value is None:
            raise ValueError(f"{Context()}::An error occured while computing node value")

        return self._value

    def clear(self) -> None:
        """
        Clear current node.
        """

        self._value = None

    def init(self, element: dict[str, Any]) -> None:
        """
        Initialize node value.

        Args:
            element (dict[str, Any]): A dictionary representing an element to be filtered.
        """

        self._value = self._node_filter.filter_dict(element)

    @override
    def __str__(self) -> str:
        """
        Convert the current node into a string.

        Returns:
            str: A string representation of the node, showing its filter and value if applicable.
        """

        res_str = ""
        if self._value is not None:
            res_str = f" => {self.compute_value()}"

        return f"(({self._node_filter}){res_str})"

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the current instance into a dict.

        Returns:
            dict[str, Any]: A dictionary representation of the node containing its flag, value, and filter.
        """

        return {"flag": self._flag, "value": self._value, "filter": str(self._node_filter)}

    # ****************************************************************
    # Static methods


class DecisionTreeNodeList(UtilsList):
    """A list of decision tree nodes."""

    def by_value(self, value: bool = True) -> "DecisionTreeNodeList":
        """
        Return a sub decision tree node list matching the given value.

        Args:
            value (bool | None): The boolean value to filter by. Defaults to True.

        Returns:
            DecisionTreeNodeList: A list of nodes with the specified value.
        """

        def node_value_eq_value(node: "DecisionTreeNode") -> bool:
            return node.compute_value() == value

        return DecisionTreeNodeList(filter(node_value_eq_value, self))

    def details_list(self) -> list[str]:
        """
        Return a list of decision tree node detail string.

        Returns:
            list[str]: A list of strings representing the nodes' details.
        """

        return list(map(str, self))

    def flags_list(self) -> list["DecisionNodeFlagType"]:
        """
        Return a list of decision tree node flags.

        Returns:
            list[DecisionNodeFlagType]: A list of the nodes' flags.
        """

        def node_flag(node: "DecisionTreeNode") -> "DecisionNodeFlagType":
            return node.flag

        return list(map(node_flag, self))


class DecisionTree:
    """
    A binary tree to handle complex condition checks from dicts and config files.

    It can contain sub decision trees and / or decision tree nodes.
    Sub trees and nodes are all contained in the tree nodes list.
    When parsing input dictionary to build the tree node type(sub tree or tree node) is determine based on wheither or not there is sub nodes.
    It joins node values with a given operator.
    """

    # ****************************************************************
    # Attributes & Constructors

    def __init__(self, tree_dict: "DecisionTreeDictionaryProps") -> None:
        """
        Create a new instance of DecisionTree.

        Args:
            tree_dict (dict[str, Any]): A dictionary representing the decision tree.

        Attributes:
            negate (bool)               : if True, the final value of the tree will be inverted
            operator (LogicalOperator)  : logical operator that joins node values
            nodes (DecisionTreeNodeList): a list of DecisionTree nodes that will determine the result of the tree
            value (bool)                : final value of the decision tree for an input element
        """

        context = Context()
        self.logger: "logging.Logger" = logging.getLogger(__name__)

        self._negate: bool = tree_dict.get("negate", False) or False
        self._operator: "LogicalOperator" = (
            LogicalOperator.find_by_key(tree_dict.get("operator", "and")) or LogicalOperator.AND
        )

        if self._operator.name not in LogicalOperator._member_names_:
            raise ValueError(f"{context}::Invalid operator provided {self._operator.name}")

        self._nodes: "DecisionTreeNodeList" = DecisionTreeNodeList()
        self.build(tree_dict)

        self._value: bool | None = None

    # ****************************************************************
    # Methods

    @property
    def nodes(self) -> "DecisionTreeNodeList":
        """
        Return decision tree nodes.

        Returns:
            DecisionTreeNodeList: A list of DecisionTreeNode instances representing the tree nodes.
        """

        return self._nodes

    @property
    def operator(self) -> "LogicalOperator":
        """
        Return decision tree operator.

        Returns:
            str: The logical operator used in the tree ("and" or "or").
        """

        return self._operator

    @operator.setter
    def operator(self, new_operator: "LogicalOperator") -> None:
        """
        Return tree operator.

        Args:
            new_operator (str): new operator value as a string
        """

        self._operator = new_operator

    def set_operator_from_str(self, new_operator: str) -> None:
        """
        Return tree operator.

        Args:
            new_operator (str): new operator value as a string
        """

        if new_operator.upper() in LogicalOperator._member_names_:
            self._operator = LogicalOperator[new_operator.upper()]

    def compute_value(self, element: dict[str, Any] | None = None) -> bool:
        """
        Return tree value.

        Args:
            element (dict[str, Any] | None): A dictionary representing the data to evaluate against the tree conditions.

        Returns:
            bool: The computed boolean value of the tree based on the conditions, or None if not yet computed.
        """

        if element:
            self.init(element)

        if self._value is None:
            return False

        return self._value if not self._negate else not self._value

    def add_node(self, node: "DecisionTreeDictionaryProps | DataFilterDictionaryProps") -> None:
        """
        Add a new node to the tree.

        Args:
            node (dict[str, Any]): the node to add to the tree
        """

        # If the provided node contains subnodes : it is a decision tree else: it is a simple node
        new_node: "DecisionTree | DecisionTreeNode" = (
            DecisionTree(node) if "nodes" in node else DecisionTreeNode(node)
        )

        self._nodes.append(new_node)

    def build(self, tree_dict: "DecisionTreeDictionaryProps") -> None:
        """
        Build tree nodes instances from input dictionary.

        Args:
            tree_dict (dict[str, Any]): input dictionary to build the tree
        """

        try:
            self._nodes.clear()
            for n in tree_dict.get("nodes", []):
                self.add_node(n)

        except DecisionTreeBuildError as e:
            self.logger.error(f"{Context()}::An error occured while building tree\n{e}")

    def init(self, element: dict[str, Any]) -> None:
        """
        Initialize tree node values.

        Args:
            element (dict[str, Any]): the dictionary to use for initialization
        """

        sub_values = [n.compute_value(element) for n in self._nodes]
        tree_value = self._operator.operation(*sub_values)

        self._value = tree_value

    def clear(self) -> None:
        """Clear the tree."""

        self._value = None
        self._nodes.clear()

    def leaves(self, leaves_value: bool | None = None) -> "DecisionTreeNodeList":
        """
        Get all leaves of the decision tree as a list of values.

        Returns:
            DecisionTreeNodeList: A list of values representing the leaf nodes of the decision tree.
        """

        context = Context()
        if self._nodes.is_empty():
            return self._nodes

        leaves = DecisionTreeNodeList()
        for n in self._nodes:
            if isinstance(n, DecisionTreeNode):
                leaves.append(n)

            elif isinstance(n, DecisionTree):
                leaves.extend(n.leaves())

            else:
                raise DecisionTreeInvalidNodeError(f"{context}::Invalid node found")

        if leaves_value is not None:
            leaves = leaves.by_value(value=leaves_value)

        return leaves

    @override
    def __str__(self) -> str:
        """
        Convert the current decision tree into a string.

        Returns:
            str: the current instance represented as a string which contains nodes own str representation joined by operators
        """

        sep = f" {self._operator} "
        return f"({sep.join(list(map(str, self._nodes)))})"

    def to_dict(self) -> dict[str, Any]:
        """
        Return a dictionary representing the current decision tree.

        Returns:
            dict[str, Any]: the current instance as a dictionary
        """

        return {
            "value": self._value,
            "negate": self._negate,
            "operator": self._operator,
            "flags": self._nodes.flags_list(),
            "details": list(map(any_to_dict, self._nodes)),
        }

    # ****************************************************************
    # Static methods
