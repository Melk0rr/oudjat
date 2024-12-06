from typing import List, Dict, Union

from oudjat.utils import ColorPrint
from oudjat.control.data import DataFilter

class DecisionTreeNode:
  """ A decision tree node """
  
  # ****************************************************************
  # Attributes & Constructors

  def __init__(self, node_dict: Dict):
    """ Constructor """

    self.flag = node_dict.get("flag", None)
    self.node_filter: DataFilter = DataFilter.datafilter_from_dict(dictionnary=node_dict)
    self.result = None

  # ****************************************************************
  # Methods
  
  def get_flag(self) -> Union[int, str]:
    """ Getter for node flag """
    return self.flag

  def get_node_filter(self) -> DataFilter:
    """ Getter for current node filter """
    return self.node_filter
  
  def get_result(self, element: Dict = None) -> bool:
    """ Get the node filter result """

    if element is None and self.result is None:
      raise ValueError("DecisionTreeNode.get_result::Node result is None, please provide a comparison element")

    if self.result is None:
      res_value = self.node_filter.filter_dict(element)
      self.result = {
        "value": res_value,
        "details": str(self.node_filter),
        "flags": self.flag
      }
    
    return self.result
  
  def __str__(self) -> str:
    """ Converts the current node into a string """
    res_str = ''
    if self.result is not None:
      res_str = f" => {self.result["value"]}"

    return f"(({self.node_filter}){res_str})"
  
  # ****************************************************************
  # Static methods

class DecisionTreeNodeList(list):
  """ A list of decision tree nodes """

  def get_by_value(self, value: bool = True) -> "DecisionTreeNodeList":
    """ Returns a sub decision tree node list matching the given value """
    return DecisionTreeNodeList(filter(lambda l: l.get_result()["value"] == value, self))
  
  def get_details_list(self) -> List[str]:
    """ Returns a list of decision tree node detail string """
    return [ n.get_result()["details"] for n in self ]

  def get_flags_list(self) -> List[Union[int, str]]:
    """ Returns a list of decision tree node flags """
    return [ n.get_result()["flags"] for n in self ]

class DecisionTree:
  """ A binary tree to  """

  # ****************************************************************
  # Attributes & Constructors

  def __init__(self, tree_dict: Dict):
    """ Constructor """
    
    self.raw = tree_dict
    self.operator = tree_dict.get("operator", "and")
    if self.operator not in ["or", "and"]:
      raise ValueError(f"Invalid operator provided: {self.operator}")
    
    self.nodes = None
    self.value = None
    self.details = None


  # ****************************************************************
  # Methods
  
  def get_nodes(self) -> List:
    """ Getter for decision tree nodes """
    return self.nodes

  def get_operator(self) -> str:
    """ Getter for decision tree operator """
    return self.operator

  def get_value(self) -> bool:
    """ Getter for tree value """
    return self.value

  def set_operator(self, new_operator: str) -> None:
    """ Setter for tree operator """

    if new_operator.lower() in ["or", "and"]:
      self.operator = new_operator.lower()

  def add_node(self, node: Dict) -> None:
    """ Adds a new node to the tree """
    
    # If the provided node contains subnodes : it is a decision tree else: it is a simple node
    if node.get("nodes", None) is not None:
      node = DecisionTree(tree_dict=node)
      node.build()

    else:
      node = DecisionTreeNode(node_dict=node)

    self.nodes.append(node)
  
  def build(self) -> None:
    """ Builds the decision tree """
    
    try:
      self.nodes = []
      for n in self.raw.get("nodes", []):
        self.add_node(n)

    except Exception as e:
      self.nodes = None
      ColorPrint.red(f"DecisionTree.build::An error occured while building tree\n{e}")

  def init(self, element: Dict) -> None:
    """ Initialize tree """
    
    # If nods have not yet been built -> build
    if self.nodes is None:
      self.build()
      
    
    details = [ n.get_result(element) for n in self.nodes ]
    sub_values = [ d["value"] for d in details ]

    tree_value = all(sub_values) if self.operator == "and" else any(sub_values)
    if tree_value and self.flag is not None:
      tree_value = self.flag
    
    self.value = tree_value
    self.details = details
      
      
  def clear(self) -> None:
    """ Clears the tree """
    self.nodes = None
    self.result = None

  def get_result(self, element: Dict, clear_result: bool = False) -> bool:
    """ Get results for each nodes in current tree and join with operator """

    if clear_result:
      self.clear()
      
    if self.result is None:
      self.init(element)

    return self.result

  def get_leaves(self) -> DecisionTreeNodeList:
    """ Returns a flattened list of decision tree nodes """

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

    return leaves
  
  def __str__(self) -> str:
    """ Converts the current decision tree into a string """
    sep = f" {self.operator.upper()} "
    return f"({sep.join([ str(n) for n in self.nodes ])})"

  
  # ****************************************************************
  # Static methods
  