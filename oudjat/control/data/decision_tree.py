from typing import Any, Dict, List, Union

from oudjat.utils.color_print import ColorPrint
from oudjat.utils.mappers import any_to_dict

from .data_filter import DataFilter


class DecisionTreeNode:
    """A decision tree node"""

    # ****************************************************************
    # Attributes & Constructors

    def __init__(self, node_dict: Dict):
        """Constructor"""

        self.flag = node_dict.get("flag", None)
        self.node_filter: DataFilter = DataFilter.from_dict(dictionnary=node_dict)
        self.node_filter.set_negate(node_dict.get("negate", False))
        self.value = None

    # ****************************************************************
    # Methods

    def get_flag(self) -> Union[int, str]:
        """Getter for node flag"""

        return self.flag

    def get_node_filter(self) -> DataFilter:
        """Getter for current node filter"""

        return self.node_filter

    def get_value(self, element: Dict = None) -> bool:
        """Getter for node value"""

        if self.value is None and element is not None:
            self.init(element)

        return self.value

    def to_dict(self) -> Dict:
        """Converts the current instance into a dict"""

        return {"flag": self.flag, "value": self.value, "filter": str(self.node_filter)}

    def clear(self) -> None:
        """Clears current node"""

        self.value = None
        del self.node_filter

    def init(self, element: Dict) -> None:
        """Initialize node value"""

        self.value = self.node_filter.filter_dict(element)

    def __str__(self) -> str:
        """Converts the current node into a string"""

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
        """Returns a sub decision tree node list matching the given value"""

        return DecisionTreeNodeList(filter(lambda node: node.get_value() == value, self))

    def get_details_list(self) -> List[str]:
        """Returns a list of decision tree node detail string"""

        return list(map(str, self))

    def get_flags_list(self) -> List[Union[int, str]]:
        """Returns a list of decision tree node flags"""

        return list(map(DecisionTreeNode.node_flag, self))



class DecisionTree:
    """A binary tree to handle complex condition checks from dicts or JSON"""

    # ****************************************************************
    # Attributes & Constructors

    def __init__(self, tree_dict: Dict):
        """Constructor"""

        self.raw = tree_dict

        # If negate is true : the tree value will be reversed (e.g. value=True => False)
        self.negate: bool = tree_dict.get("negate", False)

        # Allows to map the tree raw boolean value to a customized value (e.g. {True: "YES", False: "NO"})
        self.value_map: Dict = tree_dict.get("value_map", {True: True, False: False})

        self.operator: str = tree_dict.get("operator", "and")
        if self.operator not in ["or", "and"]:
            raise ValueError(f"Invalid operator provided: {self.operator}")

        self.nodes = None
        self.value = None

    # ****************************************************************
    # Methods

    def get_nodes(self) -> List:
        """Getter for decision tree nodes"""
        return self.nodes

    def get_operator(self) -> str:
        """Getter for decision tree operator"""
        return self.operator

    def get_value(self, element: Dict = None, clear: bool = True) -> bool:
        """Getter for tree value"""

        if clear:
            self.clear()

        if self.value is None and element is not None:
            self.init(element)

        if self.value is None:
            return None

        return self.value if not self.negate else not self.value

    def get_mapped_value(self, element: Dict = None) -> Any:
        """Get mapped value based on value, negate and value map"""

        default_value = self.get_value(element)

        if default_value is None:
            return None

        return self.value_map[default_value]

    def set_operator(self, new_operator: str) -> None:
        """Setter for tree operator"""

        if new_operator.lower() in ["or", "and"]:
            self.operator = new_operator.lower()

    def add_node(self, node: Dict) -> None:
        """Adds a new node to the tree"""

        # If the provided node contains subnodes : it is a decision tree else: it is a simple node
        if node.get("nodes", None) is not None:
            node = DecisionTree(tree_dict=node)
            node.build()

        else:
            node = DecisionTreeNode(node_dict=node)

        self.nodes.append(node)

    def build(self) -> None:
        """Builds tree nodes instances from raw dict"""

        try:
            self.nodes = []
            for n in self.raw.get("nodes", []):
                self.add_node(n)

        except Exception as e:
            self.nodes = None
            ColorPrint.red(f"DecisionTree.build::An error occured while building tree\n{e}")

    def init(self, element: Dict) -> None:
        """Initialize tree node values"""

        # If nods have not yet been built -> build
        if self.nodes is None:
            self.build()

        sub_values = [n.get_value(element) for n in self.nodes]
        tree_value = all(sub_values) if self.operator == "and" else any(sub_values)

        self.value = tree_value

    def clear(self) -> None:
        """Clears the tree"""

        self.value = None
        for n in self.nodes:
            del n

    def get_leaves(self, leaves_value: bool = None) -> DecisionTreeNodeList:
        """Returns a flattened list of decision tree nodes"""

        if self.nodes is None:
            return None

        leaves = DecisionTreeNodeList()
        for n in self.nodes:
            if isinstance(n, DecisionTreeNode):
                leaves.append(n)

            elif isinstance(n, DecisionTree):
                leaves.extend(n.get_leaves())

            else:
                raise ValueError("DecisionTree.get_leaves::Invalid node found")

        if leaves_value is not None:
            leaves = leaves.get_by_value(value=leaves_value)

        return leaves

    def __str__(self) -> str:
        """Converts the current decision tree into a string"""

        sep = f" {self.operator.upper()} "
        return f"({sep.join(list(map(str, self.nodes)))})"

    def to_dict(self) -> Dict:
        """
        Returns a dictionary representing the current decision tree
        """

        return {
            "value": self.value,
            "negate": self.negate,
            "operator": self.operator,
            "mapped_value": self.get_mapped_value(),
            "details": list(map(any_to_dict, self.nodes))
        }

    # ****************************************************************
    # Static methods


