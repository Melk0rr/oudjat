"""A module that provide a way to dynamically change behaviors or add properties to an object through decision trees."""

# TODO: fully use LogicalOperator and LogicalOperation classes

from typing import Any, TypeAlias, override

from oudjat.utils import ColorPrint, LogicalOperator
from oudjat.utils.mappers import any_to_dict
from oudjat.utils.types import NumberType

from .data_filter import DataFilter

DecisionNodeFlagType: TypeAlias = NumberType | str | None


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

    def __init__(self, node_dict: dict[str, Any]) -> None:
        """
        Create a new DecisionTree node.

        Args:
            node_dict (dict[str, Any]): A dictionary containing the initialization data for the node.

        Attributes:
            flag (DecisionNodeFlagType): flag associated with this node in case the result value is true
            node_filter (DataFilter)   : data filter of this node that will be used to compute node value for a particular input element
            value (bool)               : the current value of the node for a given element
        """

        self.flag: DecisionNodeFlagType = node_dict.get("flag", None)
        self.node_filter: DataFilter = DataFilter.from_dict(node_dict)
        self.node_filter.negate = node_dict.get("negate", False)
        self.value: bool | None = None

    # ****************************************************************
    # Methods

    def get_flag(self) -> DecisionNodeFlagType:
        """
        Return node flag.

        Returns:
            DecisionNodeFlagType: The flag of the node.
        """

        return self.flag

    def get_node_filter(self) -> DataFilter:
        """
        Return the current node filter.

        Returns:
            DataFilter: The filter associated with the node.
        """

        return self.node_filter

    def get_value(self, element: dict[str, Any] | None = None) -> bool:
        """
        Return the node value.

        Args:
            element (dict[str, Any], optional): A dictionary representing an element to be filtered. Defaults to None.

        Returns:
            bool: The value of the node after applying its filter if necessary.
        """

        if element:
            self.init(element)

        if self.value is None:
            raise ValueError(
                f"{__class__.__name__}.get_value::An error occured while computing tree value"
            )

        return self.value

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the current instance into a dict.

        Returns:
            dict[str, Any]: A dictionary representation of the node containing its flag, value, and filter.
        """

        return {"flag": self.flag, "value": self.value, "filter": str(self.node_filter)}

    def clear(self) -> None:
        """
        Clear current node.
        """

        self.value = None
        del self.node_filter

    def init(self, element: dict[str, Any]) -> None:
        """
        Initialize node value.

        Args:
            element (dict[str, Any]): A dictionary representing an element to be filtered.
        """

        self.value = self.node_filter.filter_dict(element)

    @override
    def __str__(self) -> str:
        """
        Convert the current node into a string.

        Returns:
            str: A string representation of the node, showing its filter and value if applicable.
        """

        res_str = ""
        if self.value is not None:
            res_str = f" => {self.get_value()}"

        return f"(({self.node_filter}){res_str})"

    # ****************************************************************
    # Static methods

    @staticmethod
    def node_flag(node: "DecisionTreeNode") -> DecisionNodeFlagType:
        """
        Return a node flag.

        Args:
            node (DecisionTreeNode): node to return the flag of

        Returns:
            str: node flag
        """

        return node.get_flag()


class DecisionTreeNodeList(list):
    """A list of decision tree nodes."""

    def get_by_value(self, value: bool = True) -> "DecisionTreeNodeList":
        """
        Return a sub decision tree node list matching the given value.

        Args:
            value (bool, optional): The boolean value to filter by. Defaults to True.

        Returns:
            DecisionTreeNodeList: A list of nodes with the specified value.
        """

        def node_value_eq_value(node: DecisionTreeNode) -> bool:
            return node.get_value() == value

        return DecisionTreeNodeList(filter(node_value_eq_value, self))

    def get_details_list(self) -> list[str]:
        """
        Return a list of decision tree node detail string.

        Returns:
            list[str]: A list of strings representing the nodes' details.
        """

        return list(map(str, self))

    def get_flags_list(self) -> list[DecisionNodeFlagType]:
        """
        Return a list of decision tree node flags.

        Returns:
            list[DecisionNodeFlagType]: A list of the nodes' flags.
        """

        return list(map(DecisionTreeNode.node_flag, self))

    def is_empty(self) -> bool:
        """
        Return wheither or not the list is empty.

        Returns:
            bool: True if the list is empty. False otherwise.
        """

        return len(self) == 0


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

    def __init__(self, tree_dict: dict[str, Any]) -> None:
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

        self.negate: bool = tree_dict.get("negate", False)

        # TODO: Check other references of operator (in DecisionTreeNode to)
        self.operator: LogicalOperator = tree_dict.get("operator", LogicalOperator.AND)
        if self.operator.name not in LogicalOperator._member_names_:
            raise ValueError(
                f"{__class__.__name__}::Invalid operator provided {self.operator.ope_name}"
            )

        self.nodes: DecisionTreeNodeList = DecisionTreeNodeList()
        self.build(tree_dict)

        self.value: bool | None = None

    # ****************************************************************
    # Methods

    def get_nodes(self) -> DecisionTreeNodeList:
        """
        Return decision tree nodes.

        Returns:
            DecisionTreeNodeList: A list of DecisionTreeNode instances representing the tree nodes.
        """

        return self.nodes

    def get_operator(self) -> "LogicalOperator":
        """
        Return decision tree operator.

        Returns:
            str: The logical operator used in the tree ("and" or "or").
        """

        return self.operator

    def get_value(self, element: dict[str, Any] | None = None) -> bool:
        """
        Return tree value.

        Args:
            element (dict[str, Any], optional): A dictionary representing the data to evaluate against the tree conditions.

        Returns:
            bool: The computed boolean value of the tree based on the conditions, or None if not yet computed.
        """

        if element:
            self.init(element)

        if self.value is None:
            return False

        return self.value if not self.negate else not self.value

    def set_operator(self, new_operator: str) -> None:
        """
        Return tree operator.

        Args:
            new_operator (str): new operator value as a string
        """

        if new_operator.upper() in LogicalOperator._member_names_:
            self.operator = LogicalOperator[new_operator.upper()]

    def add_node(self, node: dict[str, Any]) -> None:
        """
        Add a new node to the tree.

        Args:
            node (dict[str, Any]): the node to add to the tree
        """

        # If the provided node contains subnodes : it is a decision tree else: it is a simple node
        new_node: DecisionTree | DecisionTreeNode = (
            DecisionTree(node) if node.get("nodes", None) else DecisionTreeNode(node)
        )

        self.nodes.append(new_node)

    def build(self, tree_dict: dict[str, Any]) -> None:
        """
        Build tree nodes instances from input dictionary.

        Args:
            tree_dict (dict[str, Any]): input dictionary to build the tree
        """

        try:
            self.nodes.clear()
            for n in tree_dict.get("nodes", []):
                self.add_node(n)

        except Exception as e:
            ColorPrint.red(f"{__class__.__name__}.build::An error occured while building tree\n{e}")

    def init(self, element: dict[str, Any]) -> None:
        """
        Initialize tree node values.

        Args:
            element (dict[str, Any]): the dictionary to use for initialization
        """

        # TODO: See if all logical operators can be used
        sub_values = [n.get_value(element) for n in self.nodes]
        tree_value = all(sub_values) if self.operator == LogicalOperator.AND else any(sub_values)

        self.value = tree_value

    def clear(self) -> None:
        """Clear the tree."""

        self.value = None
        self.nodes.clear()

    def get_leaves(self, leaves_value: bool | None = None) -> DecisionTreeNodeList:
        """
        Get all leaves of the decision tree as a list of values.

        Returns:
            List: A list of values representing the leaf nodes of the decision tree.
        """

        if self.nodes.is_empty():
            return self.nodes

        leaves = DecisionTreeNodeList()
        for n in self.nodes:
            if isinstance(n, DecisionTreeNode):
                leaves.append(n)

            elif isinstance(n, DecisionTree):
                leaves.extend(n.get_leaves())

            else:
                raise ValueError(f"{__class__.__name__}.get_leaves::Invalid node found")

        if leaves_value is not None:
            leaves = leaves.get_by_value(value=leaves_value)

        return leaves

    @override
    def __str__(self) -> str:
        """
        Convert the current decision tree into a string.

        Returns:
            str: the current instance represented as a string which contains nodes own str representation joined by operators
        """

        sep = f" {self.operator} "
        return f"({sep.join(list(map(str, self.nodes)))})"

    def to_dict(self) -> dict[str, Any]:
        """
        Return a dictionary representing the current decision tree.

        Returns:
            dict[str, Any]: the current instance as a dictionary
        """

        return {
            "value": self.value,
            "negate": self.negate,
            "operator": self.operator,
            "flags": self.nodes.get_flags_list(),
            "details": list(map(any_to_dict, self.nodes)),
        }

    # ****************************************************************
    # Static methods
