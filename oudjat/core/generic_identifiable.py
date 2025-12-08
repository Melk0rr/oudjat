"""A module to describe a generic class that includes common properties among multiple asset types."""

from abc import ABC, abstractmethod
from typing import Any, TypedDict, TypeVar, override

from oudjat.utils import Context

from .exceptions import CustomAttributeError

GenericBoundType = TypeVar("GenericBoundType", bound="GenericIdentifiable")

class GenericIdentifiableBaseDict(TypedDict):
    """
    A helper class to properly handle base GenericIdentifiable dictionary attributes.

    Attributes:
        id (int | str)          : The id of the object
        name (str)              : The name of the object
        label (str | None)      : The label of the object, if any
        description (str | None): The description given to the object, if any
    """

    id: int | str
    name: str
    label: str | None
    description: str | None


class GenericIdentifiable(ABC):
    """Generic class for objects with common attributes like id, name, description and label."""

    # ****************************************************************
    # Attributes & Constructors

    def __init__(
        self,
        gid: int | str,
        name: str,
        label: str | None = None,
        description: str | None = None,
        **kwargs: Any
    ) -> None:
        """
        Create a new instance of GenericIdentifiable.

        Args:
            gid (int | str)         : The identifier of the object. Can be an integer or a string.
            name (str)              : The name of the object.
            label (str | None)      : A short text label for the object, defaults to None.
            description (str | None): A detailed description of the object, defaults to None.
            kwargs (Any)            : Any further arguments

        """

        self._id: int | str = gid
        self._name: str = name
        self._label: str | None = label
        self._description: str | None = description

        self._custom_attributes: dict[str, Any] = { **kwargs }

    # ****************************************************************
    # Methods

    @property
    def id(self) -> int | str:
        """
        Return the id of the current object.

        Returns:
            int | str: the identifier of the object.
        """

        return self._id

    @property
    def name(self) -> str:
        """
        Return the name of the generic identifiable object.

        Returns:
            str: The name of the object.
        """

        return self._name

    @property
    def label(self) -> str | None:
        """
        Getter for instance label.

        Returns:
            str: A short text label for the object.
        """

        return self._label

    @property
    def description(self) -> str | None:
        """
        Return the description of the current object.

        Returns:
            str: a string that describe the current genereic identifiable object
        """

        return self._description

    @description.setter
    def description(self, new_description: str) -> None:
        """
        Set a new value for the object description.

        Args:
            new_description (str): new description value
        """

        self._description = new_description

    @property
    def custom_attributes(self, key: str | None = None) -> dict[str, Any]:
        """
        Return the object custom attributes dictionary.

        Returns:
            dict[str, Any]: a dictionary that contains custom attributes of the current object
        """

        if key is None:
            return self._custom_attributes

        if key not in self.custom_attributes.keys():
            raise CustomAttributeError(
                f"{Context()}::{self._id} does not have a custom attribute {key}"
            )

        return self.custom_attributes[key]

    @custom_attributes.setter
    def custom_attributes(self, new_custom_attr: dict[str, Any]) -> None:
        """
        Set the custom attributes of the current object.

        Args:
            new_custom_attr (dict[str, Any]): a dictionary of custom attributes
        """

        self._custom_attributes = new_custom_attr

    def add_custom_attr(self, key: str, value: Any) -> None:
        """
        Add a new custom attribute.

        Args:
            key (str): The key for the new custom attribute.
            value (Any): The value of the new custom attribute.
        """
        # TODO: Maybe use SoucedValue to track source directly there

        self.custom_attributes[key] = value

    def add_multiple_custom_attr(self, new_custom_attr: dict[str, Any]) -> None:
        """
        Add multiple new custom attributes.

        Args:
            new_custom_attr (dict[str, Any]): A dictionary of new custom attributes to be added.
        """

        self.custom_attributes.update(new_custom_attr)

    def del_custom_attr(self, key: str) -> None:
        """
        Delete a custom attribute by key.

        Args:
            key (str): The key of the custom attribute to delete.
        """

        del self.custom_attributes[key]

    def custom_attr(self, key: str) -> Any:
        """
        Return a custom attribute by key.

        Args:
            key (str): The key of the custom attribute to return.
        """

        return self.custom_attributes[key]

    def clear_custom_attr(self) -> None:
        """
        Clear all custom attributes.
        """

        self.custom_attributes = {}

    @override
    @abstractmethod
    def __str__(self) -> str:
        """
        Convert the current instance into a string.

        Raises:
            NotImplementedError: This method must be implemented by the overloading class.

        Returns:
            str: A string representation of the object, which should be implemented in any subclass.
        """

        raise NotImplementedError(
            f"{Context()}::This method must be implemented by the overloading class"
        )

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the current instance into a dictionary.

        Returns:
            dict[str, Any]: A dictionary representation of the object, including id, name, label, description, and custom attributes.
        """

        base_dict: "GenericIdentifiableBaseDict" = {
            "id": self._id,
            "name": self._name,
            "label": self._label,
            "description": self._description,
        }

        return {
            **base_dict,
            **self.custom_attributes,
        }

    # ****************************************************************
    # Static methods

    @staticmethod
    def map_per_id(generic_list: list["GenericBoundType"]) -> dict[int | str, "GenericBoundType"]:
        """
        Map a list of GenericIdentifiable instances into a dictionary per element id.

        Args:
            generic_list (list[GenericIdentifiable]): list of GenericIdentifiable instances to map

        Returns:
            dict[int | str, GenericIdentifiable]: mapped GenericIdentifiable instances as a dictionary
        """

        return { g.id: g for g in generic_list }
