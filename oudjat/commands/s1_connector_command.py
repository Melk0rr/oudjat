"""
A command module to handle interactions to Sentinel One API through the dedicated connector.
"""

from typing import Any

from oudjat.connectors.edr.sentinelone import S1Connector
from oudjat.utils.context import Context

from .base import Base


class S1ConnectorCommand(Base):
    """
    A class to provide an access to the S1Connector.
    """

    def __init__(self, options: dict[str, Any]) -> None:
        """
        Create a new S1ConnectorCommand.

        Args:
            options (dict[str, Any]): Provided options
        """

        super().__init__(options)

        context = Context()

        self.connector: "S1Connector" = S1Connector(target=self.options["target"])

        if not (
            "username" in self.options
            and "password" in self.options
            or "creds-service" in self.options
        ):
            raise ConnectorCredentialError(
                f"{context}::No credentials were provided for the connector"
            )


