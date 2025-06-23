"""A module to describe a generic class that includes common properties among multiple asset types."""

from typing import Any, Dict, Union


class GenericIdentifiable:
    """Generic class for objects with common attributes like id, name, description and label."""

    # ****************************************************************
    # Attributes & Constructors

    def __init__(
        self,
        gid: Union[int, str],
        name: str,
        label: str = None,
        description: str = None,
    ):
        """
        Create a new instance of GenericIdentifiable.

        Args:
            gid (Union[int, str]): The identifier of the object. Can be an integer or a string.
            name (str): The name of the object.
            label (str, optional): A short text label for the object, defaults to None.
            description (str, optional): A detailed description of the object, defaults to None.
        """

        self._id = gid
        self.name = name
        self.label = label
        self.description = description

        self.custom_attributes = {}

    # ****************************************************************
    # Methods

    def get_id(self) -> Union[int, str]:
        """
        Getter for instance id.

        Returns:
            Union[int, str]: The identifier of the object.
        """

        return self._id

    def get_name(self) -> str:
        """
        Getter for instance name.

        Returns:
            str: The name of the object.
        """

        return self.name

    def get_label(self) -> str:
        """
        Getter for instance label.

        Returns:
            str: A short text label for the object.
        """

        return self.label

    def get_description(self) -> str:
        """
        Getter for instance description.

        Returns:
            str: The detailed description of the object.
        """

        return self.description

    def set_description(self, new_description: str) -> None:
        """
        Setter for instance description.

        Args:
            new_description (str): The new description to be set.
        """

        self.description = new_description

    def get_custom_attr(self, key: str = None) -> Any:
        """
        Getter for custom attributes.

        Args:
            key (str, optional): The key of the custom attribute to retrieve, defaults to None.

        Returns:
            Any: The value of the custom attribute if key is provided; otherwise, returns all custom attributes as a dictionary.
        """

        if key is not None and key not in self.custom_attributes.keys():
            raise ValueError(
                f"{__class__.__name__}.get_custom_attr::{self._id} does not have any custom attribute {key}"
            )

        return self.custom_attributes if key is None else self.custom_attributes[key]

    def set_custom_attr(self, new_custom_attr: Dict[str, Any]) -> None:
        """
        Setter for custom attributes.

        Args:
            new_custom_attr (Dict[str, Any]): A dictionary of new custom attributes to be set.
        """

        self.custom_attributes = new_custom_attr

    def add_custom_attr(self, key: str, value: Any) -> None:
        """
        Add a new custom attribute.

        Args:
            key (str): The key for the new custom attribute.
            value (Any): The value of the new custom attribute.
        """

        self.custom_attributes[key] = value

    def add_multiple_custom_attr(self, new_custom_attr: Dict[str, Any]) -> None:
        """
        Add multiple new custom attributes.

        Args:
            new_custom_attr (Dict[str, Any]): A dictionary of new custom attributes to be added.
        """

        self.custom_attributes.update(new_custom_attr)

    def del_custom_attr(self, key: str) -> None:
        """
        Delete a custom attribute by key.

        Args:
            key (str): The key of the custom attribute to delete.
        """

        del self.custom_attributes[key]

    def clear_custom_attr(self) -> None:
        """
        Clear all custom attributes.
        """

        self.custom_attributes = {}

    def __str__(self) -> str:
        """
        Convert the current instance into a string.

        Raises:
            NotImplementedError: This method must be implemented by the overloading class.

        Returns:
            str: A string representation of the object, which should be implemented in any subclass.
        """

        raise NotImplementedError(
            f"{__class__.__name__}.__str__::This method must be implemented by the overloading class"
        )

    def to_dict(self) -> Dict:
        """
        Convert the current instance into a dictionary.

        Returns:
            Dict: A dictionary representation of the object, including id, name, label, description, and custom attributes.
        """

        return {
            "id": self._id,
            "name": self.name,
            "label": self.label,
            "description": self.description,
            **self.custom_attributes,
        }
