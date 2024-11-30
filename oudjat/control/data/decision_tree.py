from typing import List, Dict

from oudjat.control.data import DataFilter

class DecisionTreeNode:
  """ A decision tree node """
  
  # ****************************************************************
  # Attributes & Constructors

  def __init__(self, node_dict: Dict):
    """ Constructor """

    self.node_filter: DataFilter = DataFilter.datafilter_from_dict(dictionnary=node_dict)

  # ****************************************************************
  # Methods

  def get_node_filter(self) -> DataFilter:
    """ Getter for current node filter """
    return self.node_filter
  
  def get_result(self, element: Dict) -> bool:
    """ Get the node filter result """
    return {
      "value": self.node_filter.filter_dict(element),
      "details": str(self.node_filter)
    }
  
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
    self.results = None

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
    details = [ n.get_result(element) for n in self.nodes ]
    values = [ d["value"] for d in details ]
    
    self.results = {
      "value": all(values) if self.operator == "and" else any(values),
      "details": details
    }

    return self.results

  
  # ****************************************************************
  # Static methods
  

