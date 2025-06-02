"""Temporary (or not) module to define some base LDAP account types."""

from enum import Enum
from typing import Dict

from oudjat.control.data import DecisionTree

from .definitions import PERSON_REG


class LDAPUserType:
    """An experimental class to describe an LDAP user type."""

    # ****************************************************************
    # Attributes & Constructors

    def __init__(self, name: str, description: str, tree_dict: Dict = None) -> None:
        """
        Create a new instance of LDAPUserType.

        Args:
            name (str)       : the name of the new type
            description (str): a description of the new type
            tree_dict (Dict) : a decision tree as a dictionary to describe what values in an LDAPUser will match the type
        """

        self.name = name
        self.description = description

        self.decision_tree = None
        self.set_decision_tree(new_decision_tree=tree_dict)

    # ****************************************************************
    # Methods

    def get_name(self) -> str:
        """
        Return the user type name.

        Returns:
            str: name of the type
        """

        return self.name

    def get_description(self) -> str:
        """
        Return the user type description.

        Returns:
            str: description of the type
        """

    def get_decision_tree(self) -> DecisionTree:
        """
        Return the type decision tree.

        Returns:
            DecisionTree: decision tree instance bound to the current type
        """
        return self.decision_tree

    def set_decision_tree(self, new_decision_tree: DecisionTree) -> None:
        """
        Set the user type decision tree.

        Args:
            new_decision_tree (DecisionTree): new decision tree to use for the current type
        """

        if isinstance(new_decision_tree, DecisionTree):
            self.decision_tree = new_decision_tree
            self.decision_tree.build()


class BaseLDAPUserType(Enum):
    """An enumeration to define some base user types."""

    PERSON = LDAPUserType(
        name="PERSON",
        description="User account binded to a physical person",
        tree_dict={
            "operator": "or",
            "nodes": [
                {"fieldname": "employeeID", "operator": "isnt", "value": None},
                {
                    "operator": "and",
                    "nodes": [
                        {"fieldname": "sn", "operator": "match", "value": PERSON_REG},
                        {"fieldname": "givenName", "operator": "match", "value": PERSON_REG},
                    ],
                },
            ],
        },
    )

    SERVICE = LDAPUserType(
        name="SERVICE",
        description="User account used to run a service or for application purposes",
        tree_dict={
            "operator": "or",
            "nodes": [
                {"fieldname": "sAMAccountName", "operator": "match", "value": r"^svc[-_].*$"},
                {
                    "fieldname": "distinguishedName",
                    "operator": "search",
                    "value": r"OU=Service Accounts|OU=Services,OU=Users,DC=",
                },
            ],
        },
    )

    GENERIC = LDAPUserType(
        name="GENERIC", description="User account used by multiple persons", tree_dict=None
    )

