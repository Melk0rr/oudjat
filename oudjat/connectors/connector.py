from typing import Any, List

from oudjat.utils import CredentialHelper


class Connector:
    """
    This class serves as a base for any type of connector
    A connector can be seen as a hook to a data source that is used to pull/extract data from it
    """

    def __init__(
        self, target: Any, service_name: str = None, use_credentials: bool = False
    ) -> None:
        """
        Creates a new instance of Connector

        Args:
            target (any)            : connector target
            service_name (str)      : service name to associate with the connector, will be used to register credentials
            use_credentials (bool)  : wheither the connector should use credentials
        """

        self.target = target
        self.service_name = service_name

        # Retreive credentials for the service
        self.credentials = CredentialHelper.get_credentials(self.service_name) if use_credentials else None
        self.connection = None

    def get_connection(self) -> Any:
        """
        Returns the current connection

        Args:
            None

        Return:
            any : active connection
        """

        return self.connection

    def set_target(self, target: Any) -> None:
        """
        Setter for connector target

        Args:
            target (any) : new target of the connector
        """

        self.target = target

    def set_service_name(self, new_service_name: str, use_credentials: bool) -> None:
        """
        Setter for service name

        Args:
            new_service_name (str) : new service name for the connector
            use_credentials (bool) : wheither the connector should use credentials

        Return:
            None
        """

        self.service_name = new_service_name

        if use_credentials:
            self.credentials = CredentialHelper.get_credentials(self.service_name)

    def connect(self) -> None:
        """
        Connects to the target

        Args:
            None

        Return:
            None
        """

        raise NotImplementedError(
            f"{__class__.__name__}.connect::Method must be implemented by the overloading class"
        )

    def search(self) -> List[Any]:
        """
        Connects to the target

        Args:
            None

        Return:
            List[any] : list of results
        """

        raise NotImplementedError(
            f"{__class__.__name__}.search::Method must be implemented by the overloading class"
        )
