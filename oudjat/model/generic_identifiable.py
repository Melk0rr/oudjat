from typing import Dict, Union, Any


class GenericIdentifiable:
    """Generic class for objects with common attributes like id, name, description and label"""

    # ****************************************************************
    # Attributes & Constructors

    def __init__(
        self,
        id: Union[int, str],
        name: str,
        label: str = None,
        description: str = None,
    ):
        """Constructor"""

        self.id = id
        self.name = name
        self.label = label
        self.description = description

        self.custom_attributes = {}

    # ****************************************************************
    # Methods

    def get_id(self) -> Union[int, str]:
        """Getter for instance id"""
        return self.id

    def get_name(self) -> str:
        """Getter for instance name"""
        return self.name

    def get_label(self) -> str:
        """Getter for instance label"""
        return self.label

    def get_description(self) -> str:
        """Getter for instance description"""
        return self.description

    def set_description(self, new_description: str) -> None:
        """Setter for instance description"""
        self.description = new_description

    def get_custom_attr(self, key: str = None) -> Any:
        """Getter for custom attributes"""
        if key is None:
            return self.custom_attributes

        return self.custom_attributes[key]

    def set_custom_attr(self, new_custom_attr: Dict[str, Any]) -> None:
        """Setter for custom attributes"""
        self.custom_attributes = new_custom_attr

    def add_custom_attr(self, key: str, value: Any) -> None:
        """Adds a new custom attribute"""
        self.custom_attributes[key] = value

    def add_multiple_custom_attr(self, new_custom_attr: Dict[str, Any]) -> None:
        """Adds multiple new custom attributes"""
        self.custom_attributes.update(new_custom_attr)

    def del_custom_attr(self, key: str) -> None:
        """Deletes a custom attribute by key"""
        del self.custom_attributes[key]

    def clear_custom_attr(self) -> None:
        """Clears custom attributes"""
        self.custom_attributes = {}

    def __str__(self) -> str:
        """Converts the current instance into a string"""
        raise NotImplementedError("__str__() method must be implemented by the overloading class")

    def to_dict(self) -> Dict:
        """Converts the current instance into a dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "label": self.label,
            "description": self.description,
            **self.custom_attributes,
        }

