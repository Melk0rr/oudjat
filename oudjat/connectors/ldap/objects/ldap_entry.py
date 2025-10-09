"""A module to handle LDAP query results: LDAP entries."""

from typing import Any, override

from .ldap_object_types import LDAPObjectType


class LDAPEntry(dict):
    """A class that describe a result of an LDAP query."""

    @property
    def dn(self) -> str:
        """
        Return the Distinguished Name (DN) of the LDAP entry.

        The DN is retrieved from the "dn" key in the dictionary representation of the LDAP entry.

        Returns:
            str: The DN of the LDAP entry.
        """

        return self.__getitem__("dn")

    @property
    def id(self) -> str:
        """
        Return the GUID of the current LDAP entry.

        Returns:
            str: object GUID string
        """

        return self.get("objectGUID")


    @property
    def name(self) -> str:
        """
        Return the name of the current LDAP entry.

        Returns:
            str: object name
        """

        return self.get("name")

    @property
    def description(self) -> str:
        """
        Return the description of the current LDAP entry.

        Returns:
            str: object description string
        """

        return self.get("description")

    @property
    def attr(self) -> dict[str, Any]:
        """
        Return the "attributes" dictionary of the LDAP entry.

        Returns:
            dict: The "attributes" dictionary containing all the attributes of the LDAP entry.
        """

        return self.__getitem__("attributes")

    @property
    def type(self) -> str:
        """
        Determine the object type of the LDAP entry based on its "objectClass" attribute.

        Returns:
            str: The name of the object class, or None if no matching class is found.
        """

        obj_type = next(filter(self.compare_to_obj_type_cls, list(LDAPObjectType)))
        return obj_type.name or None

    @override
    def get(self, key: str, default_value: Any = None) -> Any:
        """
        Retrieve the value of the specified attribute.

        If the attribute is not present in the "attributes" dictionary, or if it is a list with no elements, returns the provided default value.

        Args:
            key (str)                    : The attribute key to retrieve.
            default_value (Any, optional): The value to return if the attribute is not found or is an empty list. Defaults to None.

        Returns:
            Any: The value of the specified attribute or the default value if not found or empty.
        """

        if key not in self.__getitem__("attributes").keys():
            return default_value

        item = self.__getitem__("attributes").__getitem__(key)

        if isinstance(item, list) and len(item) == 0:
            return None

        return item

    def set(self, key: str, value: Any) -> Any:
        """
        Set the specified attribute to the given value in the "attributes" dictionary.

        Args:
            key (str)   : The attribute key to set.
            value (Any) : The value to assign to the attribute.

        Returns:
            Any: The value that was assigned to the attribute.
        """

        return self.__getitem__("attributes").__setitem__(key, value)

    def get_raw(self, key: str) -> Any:
        """
        Retrieve the value of the specified raw attribute.

        If the attribute is not present in the "raw_attributes" dictionary, returns None.

        Args:
            key (str): The raw attribute key to retrieve.

        Returns:
            Any: The value of the specified raw attribute or None if not found.
        """

        if key not in self.__getitem__("raw_attributes").keys():
            return None

        return self.__getitem__("raw_attributes").__getitem__(key)

    def is_of_class(self, obj_cls: str) -> bool:
        """
        Check whether the "objectClass" attribute in the "attributes" dictionary contains with the provided class.

        Args:
            obj_cls (str): The class to check against the "objectClass" attribute.

        Returns:
            bool: True if the object is of the specified class, False otherwise.
        """

        return obj_cls.lower() in self.attr.__getitem__("objectClass")


    def compare_to_obj_type_cls(self, object_type: LDAPObjectType) -> bool:
        """
        Compare current entry objectClass and the provided LDAPObjectType objectClass attribute.

        Args:
            object_type (LDAPObjectType): element containing the objectClass attribute to compare

        Returns:
            bool: True if both values are equals, False otherwise
        """

        return self.attr.__getitem__("objectClass")[-1] == object_type.object_cls
