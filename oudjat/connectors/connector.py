"""A module to centralize common behavior accross all connectors."""

from keyring.credentials import Credential, SimpleCredential

from oudjat.utils import CredentialHelper


class Connector:
    """
    A class serves as a base for any type of connector.

    A connector can be seen as a hook to a data source that is used to pull/extract data from it.
    """

    def __init__(
        self, target: str | object, service_name: str | None = None, use_credentials: bool = False
    ) -> None:
        """
        Create a new instance of Connector.

        Args:
            target (any)            : connector target
            service_name (str)      : service name to associate with the connector, will be used to register credentials
            use_credentials (bool)  : wheither the connector should use credentials
        """

        self.target: str | object = target
        self.service_name: str | None = service_name

        # Retrieve credentials for the service
        self.credentials: SimpleCredential | Credential | None = None
        if use_credentials and self.service_name is not None:
            self.credentials = CredentialHelper.get_credentials(self.service_name)

        self.connection: object = None

    def get_connection(self) -> object:
        """
        Return the current connection.

        Args:
            None

        Return:
            any : active connection
        """

        return self.connection

    def set_target(self, target: str | object) -> None:
        """
        Set the connection target.

        Args:
            target (any) : new target of the connector
        """

        self.target = target

    def set_service_name(self, new_service_name: str, use_credentials: bool) -> None:
        """
        Set the service name bound to the current connector.

        Args:
            new_service_name (str) : new service name for the connector
            use_credentials (bool) : wheither the connector should use credentials

        Return:
            None
        """

        self.service_name = new_service_name

        if use_credentials:
            self.credentials = CredentialHelper.get_credentials(self.service_name)

    def connect(self, *args: tuple[object], **kwargs: dict[str, object]) -> None:
        """
        Connect to the target.

        Args:
            *args (tuple)  : any args the overriding method provides
            **kwargs (dict): any kwargs the overriding method provides

        Return:
            None
        """

        raise NotImplementedError(
            f"{__class__.__name__}.connect({args}, {kwargs})::Method must be implemented by the overloading class"
        )

    def search(self, *args: tuple[object], **kwargs: dict[str, object]) -> list[str | object]:
        """
        Retrieve data from the target.

        Args:
            *args (tuple)  : any args the overriding method provides
            **kwargs (dict): any kwargs the overriding method provides

        Return:
            list[any] : list of results
        """

        raise NotImplementedError(
            f"{__class__.__name__}.search({args}, {kwargs})::Method must be implemented by the overloading class"
        )
