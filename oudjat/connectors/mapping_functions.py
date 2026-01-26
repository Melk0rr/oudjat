"""
A module that list asset mapping functions.
"""

from enum import Enum
from typing import Any

from oudjat.core.software.os import OSFamily

from .asset_mapper import AssetMapper


class MappingFunction(Enum):
    """
    An enumeration of asset mapping functions per category/asset type.
    """

    OS = {
        "os_from_str": AssetMapper.guess_os,
        "os_family_from_str": OSFamily.search_os_family_opt,
        "os_edition_from_str": AssetMapper.guess_os_edition,
        "os_release_from_str": AssetMapper.guess_os_release,
        "os_details_from_str": AssetMapper.map_os
    }

    def __call__(self, function_name: str, **kwargs: Any) -> Any:
        """
        Call a mapping function based on its name.

        Args:
            function_name (str): The name of the function to call
            **kwargs (Any)     : Arguments to pass to the called function

        Returns:
            Any: Whatever the called function returns
        """

        return self._value_[function_name](**kwargs)
