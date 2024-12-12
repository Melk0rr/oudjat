from enum import Enum
from typing import List, Dict

from oudjat.control.data import DecisionTree

from . import PERSON_REG

class LDAPUserType:

  # ****************************************************************
    # Attributes & Constructors

  def __init__(self, name: str, description: str, tree_dict: Dict = None):
    """ Constructor """

    self.name = name
    self.description = description
    
    self.decision_tree = None
    self.set_decision_tree(new_decision_tree=tree_dict)

  # ****************************************************************
  # Methods

  def get_name(self) -> str:
    """ Getter for user type name """
    return self.name
  
  def get_description(self) -> str:
    """ Getter for user type description """
    
  def get_decision_tree(self) -> DecisionTree:
    """ Getter for user type decision tree """
    return self.decision_tree
  
  def set_decision_tree(self, new_decision_tree: DecisionTree) -> None:
    """ Setter for user type decision tree """
    
    if isinstance(new_decision_tree, DecisionTree):
      self.decision_tree = new_decision_tree
      self.decision_tree.build()

class BaseLDAPUserType(Enum):
  PERSON = LDAPUserType(
    name="PERSON",
    description="User account binded to a physical person",
    tree_dict={
      "operator": "or",
      "nodes": [
        {
          "fieldname": "employeeID",
          "operator": "isnt",
          "value": None
        },
        {
          "operator": "and",
          "nodes": [
            {
              "fieldname": "sn",
              "operator": "match",
              "value": PERSON_REG
            },
            {
              "fieldname": "givenName",
              "operator": "match",
              "value": PERSON_REG
            },
          ]
        }
      ]
    }
  )

  SERVICE = LDAPUserType(
    name="SERVICE",
    description="User account used to run a service or for application purposes",
    tree_dict={
      "operator": "or",
      "nodes": [
        {
          "fieldname": "sAMAccountName",
          "operator": "match",
          "value": r'^svc[-_].*$'
        },
        {
          "fieldname": "distinguishedName",
          "operator": "search",
          "value": r'OU=Service Accounts|OU=Services,OU=Users,DC='
        }
      ]
    }
  )

  GENERIC = LDAPUserType(
    name="GENERIC",
    description="User account used by multiple persons",
    tree_dict=None
  )