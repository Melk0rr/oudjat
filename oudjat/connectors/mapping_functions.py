"""
A module that list asset mapping functions.
"""

from enum import Enum
from typing import Any

from oudjat.core.software.os import OSFamily

from .asset_mapper import AssetMapper


class OSMappingFunction(Enum):
    """
    An enumeration of OS specific mapping functions.
    """

    OS_FROM_STR = AssetMapper.guess_os
    OS_FAMILY_FROM_STR = OSFamily.search_os_family_opt
    OS_EDITION_FROM_STR = AssetMapper.guess_os_edition
    OS_RELEASE_FROM_STR = AssetMapper.guess_os_release
    OS_DETAILS_FROM_STR = AssetMapper.map_os

    def __call__(self, function_name: str, **kwargs: Any) -> Any:
        """
        Call a mapping function based on its name.

        Args:
            function_name (str): The name of the function to call
            **kwargs (Any)     : Arguments to pass to the called function

        Returns:
            Any: Whatever the called function returns
        """

        return self._value_(**kwargs)


class MappingFunction(Enum):
    """
    An enumeration of asset mapping functions per category/asset type.
    """

    OS = OSMappingFunction

    def __call__(self, func: str, **kwargs: Any) -> Any:
        """
        Call a mapping function based on its name.

        Args:
            func (str)    : The name of the function to call
            **kwargs (Any): Arguments to pass to the called function

        Returns:
            Any: Whatever the called function returns
        """

        return self._value_[func.upper()](**kwargs)
