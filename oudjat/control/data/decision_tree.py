from typing import List, Dict

from oudjat.control.data import DataFilter

class DecisionTreeNode:
  """ A decision tree node """
  
  # ****************************************************************
  # Attributes & Constructors

  def __init__(self, node_dict: Dict):
    """ Constructor """

    self.node_filter: DataFilter = DataFilter.datafilter_from_dict(dictionnary=node_dict)
    self.result = None

  # ****************************************************************
  # Methods

  def get_node_filter(self) -> DataFilter:
    """ Getter for current node filter """
    return self.node_filter
  
  def get_result(self, element: Dict = None) -> bool:
    """ Get the node filter result """

    if element is None and self.result is None:
      raise ValueError("DecisionTreeNode.get_result::Node result is None, please provide a comparison element")

    if self.result is None:
      self.result = {
        "value": self.node_filter.filter_dict(element),
        "details": str(self.node_filter)
      }
    
    return self.result
  
  def __str__(self) -> str:
    """ Converts the current node into a string """
    res_str = ''
    if self.result is not None:
      res_str = f" = {self.result["value"]}"

    return f"(({self.node_filter}){res_str})"
  
  # ****************************************************************
  # Static methods

class DecisionTree:
  """ A binary tree to  """

  # ****************************************************************
  # Attributes & Constructors

  def __init__(self, tree_dict: Dict):
    """ Constructor """
    
    self.operator = tree_dict.get("operator", "and")
    self.nodes = tree_dict.get("nodes", [])
    self.result = None

  # ****************************************************************
  # Methods
  
  def get_nodes(self) -> List:
    """ Getter for decision tree nodes """
    return self.nodes

  def get_operator(self) -> str:
    """ Getter for decision tree operator """
    return self.operator
  
  def build(self) -> None:
    """ Builds the decision tree """
    
    built_nodes = []
    for n in self.nodes:
      if n.get("nodes", None) is not None:
        n = DecisionTree(tree_dict=n)
        n.build()

      else:
        n = DecisionTreeNode(node_dict=n)

      built_nodes.append(n)
      
    self.nodes = built_nodes

  def get_result(self, element: Dict) -> bool:
    """ Get results for each nodes in current tree and join with operator """

    if self.result is None:
      details = [ n.get_result(element) for n in self.nodes ]
      values = [ d["value"] for d in details ]
      
      self.result = {
        "value": all(values) if self.operator == "and" else any(values),
        "details": details,
      }

    return self.result

  def get_result_matches(self) -> bool:
    """ Get a flat list of the true assesments in the tree """
    
    if self.result is None:
      return None

    res = []
    for n in self.nodes:
      if isinstance(n, DecisionTreeNode):
        if n.get_result()["value"] is True:
          res.append(str(n.get_node_filter()))
          
      elif isinstance(n, DecisionTree):
        res.extend(n.get_result_matches())
        
    return res
  
  def __str__(self) -> str:
    """ Converts the current decision tree into a string """
    sep = f" {self.operator.upper()} "
    return f"({sep.join([ str(n) for n in self.nodes ])})"

  
  # ****************************************************************
  # Static methods
  

