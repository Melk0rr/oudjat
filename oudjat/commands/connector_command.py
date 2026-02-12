"""
A command module to address some shared behaviors accross connector commands.
"""

from typing import Any

from oudjat.connectors.exceptions import ConnectorCredentialError
from oudjat.utils.context import Context

from .base import Base


class ConnectorCommand(Base):
    """
    A class that handles shared properties and behaviors across connector commands.
    """

    def __init__(self, options: dict[str, Any], need_credentials: bool = False) -> None:

        super().__init__(options)

        context = Context()

        if need_credentials and not (
            ("--username" in self.options and "--password" in self.options)
            or "--creds-service" in self.options
        ):
            raise ConnectorCredentialError(
                f"{context}::No credentials were provided for the connector"
            )



