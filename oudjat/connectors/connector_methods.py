"""
A simple module to list valid HTTP connection methods.
"""

from enum import Enum
from typing import Any, Callable

import requests


class ConnectorMethod(Enum):
    """An enumeration of valid connector method values."""

    GET = "get"
    POST = "post"
    PUT = "put"

    @property
    def func(self) -> Callable[..., requests.Response]:
        """
        Return the request method based on the element value.

        Returns:
            Callable[..., Response]: HTTP requests method
        """

        return getattr(requests, self._value_)

    def __call__(self, *args: Any, **kwargs: Any) -> requests.Response:
        """
        Make the ConnectorMethod element callable.

        Args:
            args (Any)  : Any additional non-named argument
            kwargs (Any): Any additional named argument

        Returns:
            Response: HTTP request response
        """

        return self.func(*args, **kwargs)
