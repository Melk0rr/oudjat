# TODO: fully use LogicalOperator and LogicalOperation classes

from typing import Any, Dict, List, Union

from oudjat.utils import ColorPrint, LogicalOperator
from oudjat.utils.mappers import any_to_dict

from .data_filter import DataFilter


class DecisionTreeNode:
    """A decision tree node"""

    # ****************************************************************
    # Attributes & Constructors

    def __init__(self, node_dict: Dict) -> None:
        """
        Creates a new decision tree node instance

        Args:
            node_dict (Dict): A dictionary containing the initialization data for the node.
        """

        self.flag = node_dict.get("flag", None)
        self.node_filter: DataFilter = DataFilter.from_dict(dictionnary=node_dict)
        self.node_filter.set_negate(node_dict.get("negate", False))
        self.value = None

    # ****************************************************************
    # Methods

    def get_flag(self) -> Union[int, str]:
        """
        Getter for node flag

        Returns:
            Union[int, str]: The flag of the node.
        """

        return self.flag

    def get_node_filter(self) -> DataFilter:
        """
        Getter for current node filter

        Returns:
            DataFilter: The filter associated with the node.
        """

        return self.node_filter

    def get_value(self, element: Dict = None) -> bool:
        """
        Returns the node value

        Args:
            element (Dict, optional): A dictionary representing an element to be filtered. Defaults to None.

        Returns:
            bool: The value of the node after applying its filter if necessary.
        """

        if self.value is None and element is not None:
            self.init(element)

        return self.value

    def to_dict(self) -> Dict:
        """
        Converts the current instance into a dict

        Returns:
            Dict: A dictionary representation of the node containing its flag, value, and filter.
        """

        return {"flag": self.flag, "value": self.value, "filter": str(self.node_filter)}

    def clear(self) -> None:
        """
        Clears current node
        """

        self.value = None
        del self.node_filter

    def init(self, element: Dict) -> None:
        """
        Initialize node value

        Args:
            element (Dict): A dictionary representing an element to be filtered.
        """

        self.value = self.node_filter.filter_dict(element)

    def __str__(self) -> str:
        """
        Converts the current node into a string

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
    def node_flag(node: "DecisionTreeNode") -> str:
        """
        Returns a node flag

        Args:
            node (DecisionTreeNode): node to return the flag of

        Returns:
            str: node flag
        """

        return node.get_flag()


class DecisionTreeNodeList(list):
    """A list of decision tree nodes"""

    def get_by_value(self, value: bool = True) -> "DecisionTreeNodeList":
        """Returns a sub decision tree node list matching the given value

        Args:
            value (bool, optional): The boolean value to filter by. Defaults to True.

        Returns:
            DecisionTreeNodeList: A list of nodes with the specified value.
        """

        return DecisionTreeNodeList(filter(lambda node: node.get_value() == value, self))

    def get_details_list(self) -> List[str]:
        """Returns a list of decision tree node detail string

        Returns:
            List[str]: A list of strings representing the nodes' details.
        """

        return list(map(str, self))

    def get_flags_list(self) -> List[Union[int, str]]:
        """Returns a list of decision tree node flags

        Returns:
            List[Union[int, str]]: A list of the nodes' flags.
        """

        return list(map(DecisionTreeNode.node_flag, self))


class DecisionTree:
    """A binary tree to handle complex condition checks from dicts or JSON"""

    # ****************************************************************
    # Attributes & Constructors

    def __init__(self, tree_dict: Dict) -> None:
        """
        Creates a new instance of DecisionTree

        Args:
            tree_dict (Dict): A dictionary representing the decision tree.
        """

        self.raw = tree_dict

        # If negate is true : the tree value will be reversed (e.g. value=True => False)
        self.negate: bool = tree_dict.get("negate", False)

        # Allows to map the tree raw boolean value to a customized value (e.g. {True: "YES", False: "NO"})
        self.value_map: Dict = tree_dict.get("value_map", {True: True, False: False})

        # TODO: Check other references of operator (in DecisionTreeNode to)
        self.operator: LogicalOperator = tree_dict.get("operator", LogicalOperator.AND)
        if self.operator.name not in LogicalOperator._member_names_:
            raise ValueError(
                f"{__class__.__name__}::Invalid operator provided {self.operator.ope_name}"
            )

        self.nodes = None
        self.value = None

    # ****************************************************************
    # Methods

    def get_nodes(self) -> List:
        """
        Getter for decision tree nodes

        Returns:
            List: A list of DecisionTreeNode instances representing the tree nodes.
        """

        return self.nodes

    def get_operator(self) -> str:
        """
        Getter for decision tree operator

        Returns:
            str: The logical operator used in the tree ("and" or "or").
        """

        return self.operator

    def get_value(self, element: Dict = None, clear: bool = True) -> bool:
        """
        Getter for tree value

        Args:
            element (Dict, optional): A dictionary representing the data to evaluate against the tree conditions.
            clear (bool, optional): Whether to clear the current value before computing a new one.

        Returns:
            bool: The computed boolean value of the tree based on the conditions, or None if not yet computed.
        """

        if clear:
            self.clear()

        if self.value is None and element is not None:
            self.init(element)

        if self.value is None:
            return False

        return self.value if not self.negate else not self.value

    def get_mapped_value(self, element: Dict = None) -> Any:
        """
        Get mapped value based on value, negate and value map

        Args:
            element (Dict, optional): A dictionary representing the data to evaluate against the tree conditions.

        Returns:
            Any: The mapped value based on the current value, negate, and value_map attributes.
        """

        default_value = self.get_value(element)

        if default_value is None:
            return None

        return self.value_map[default_value]

    def set_operator(self, new_operator: str) -> None:
        """
        Setter for tree operator

        Args:
            new_operator (str): new operator value as a string
        """

        if new_operator.upper() in LogicalOperator._member_names_:
            self.operator = LogicalOperator[new_operator.upper()]

    def add_node(self, node: Dict) -> None:
        """
        Adds a new node to the tree

        Args:
            node (Dict): the node to add to the tree
        """

        # If the provided node contains subnodes : it is a decision tree else: it is a simple node
        if node.get("nodes", None) is not None:
            node = DecisionTree(tree_dict=node)
            node.build()

        else:
            node = DecisionTreeNode(node_dict=node)

        self.nodes.append(node)

    def build(self) -> None:
        """
        Builds tree nodes instances from raw dict
        """

        try:
            self.nodes = []
            for n in self.raw.get("nodes", []):
                self.add_node(n)

        except Exception as e:
            self.nodes = None
            ColorPrint.red(f"{__class__.__name__}.build::An error occured while building tree\n{e}")

    def init(self, element: Dict) -> None:
        """
        Initializes tree node values

        Args:
            element (Dict): the dictionary to use for initialization
        """

        # If nods have not yet been built -> build
        if self.nodes is None:
            self.build()

        # TODO: See if all logical operators can be used
        sub_values = [n.get_value(element) for n in self.nodes]
        tree_value = all(sub_values) if self.operator.ope_name == "and" else any(sub_values)

        self.value = tree_value

    def clear(self) -> None:
        """
        Clears the tree
        """

        self.value = None
        for n in self.nodes:
            del n

    def get_leaves(self, leaves_value: bool = None) -> DecisionTreeNodeList:
        """
        Get all leaves of the decision tree as a list of values

        Returns:
            List: A list of values representing the leaf nodes of the decision tree.
        """

        if self.nodes is None:
            return None

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

    def __str__(self) -> str:
        """
        Converts the current decision tree into a string

        Returns:
            str: the current instance represented as a string which contains nodes own str representation joined by operators
        """

        sep = f" {self.operator.upper()} "
        return f"({sep.join(list(map(str, self.nodes)))})"

    def to_dict(self) -> Dict:
        """
        Returns a dictionary representing the current decision tree

        Returns:
            Dict: the current instance as a dictionary
        """

        return {
            "value": self.value,
            "negate": self.negate,
            "operator": self.operator,
            "mapped_value": self.get_mapped_value(),
            "details": list(map(any_to_dict, self.nodes)),
        }

    # ****************************************************************
    # Static methods
