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
      res_value = self.node_filter.filter_dict(element)
      self.result = {
        "value": res_value,
        "details": str(self.node_filter)
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

class DecisionTree:
  """ A binary tree to  """

  # ****************************************************************
  # Attributes & Constructors

  def __init__(self, tree_dict: Dict):
    """ Constructor """
    
    self.raw = tree_dict
    self.operator = tree_dict.get("operator", "and")
    
    self.nodes = None
    self.result = None


  # ****************************************************************
  # Methods
  
  def get_nodes(self) -> List:
    """ Getter for decision tree nodes """
    return self.nodes

  def get_operator(self) -> str:
    """ Getter for decision tree operator """
    return self.operator

  def set_operator(self, new_operator: str) -> None:
    """ Setter for tree operator """

    if new_operator.lower() in ["or", "and"]:
      self.operator = new_operator.lower()

  def add_node(self, node: Dict) -> None:
    """ Adds a new node to the tree """
    # TODO
  
  def build(self) -> None:
    """ Builds the decision tree """
    
    built_nodes = []
    for n in self.raw.get("nodes", []):
      if n.get("nodes", None) is not None:
        n = DecisionTree(tree_dict=n)
        n.build()

      else:
        n = DecisionTreeNode(node_dict=n)

      built_nodes.append(n)
      
    self.nodes = built_nodes

  def clear(self) -> None:
    """ Clears the tree """
    self.nodes = None
    self.result = None

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

      else:
        raise ValueError()  

    return res
  
  def __str__(self) -> str:
    """ Converts the current decision tree into a string """
    sep = f" {self.operator.upper()} "
    return f"({sep.join([ str(n) for n in self.nodes ])})"

  
  # ****************************************************************
  # Static methods
  

