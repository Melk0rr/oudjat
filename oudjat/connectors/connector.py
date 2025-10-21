"""A module to centralize common behavior accross all connectors."""

from abc import ABC, abstractmethod
from typing import Any

from keyring.credentials import Credential, SimpleCredential

from oudjat.utils import CredentialHelper


class Connector(ABC):
    """
    A class serves as a base for any type of connector.

    A connector can be seen as a hook to a data source that is used to pull/extract data from it.
    """

    # ****************************************************************
    # Attributes & Constructors

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

        self._target: Any = target
        self._service_name: str | None = service_name

        # Retrieve credentials for the service
        self._credentials: SimpleCredential | Credential | None = None
        if use_credentials and self._service_name is not None:
            self._credentials = CredentialHelper.get_credentials(self._service_name)

        self._connection: Any = None

    # ****************************************************************
    # Methods

    @property
    def connection(self) -> object:
        """
        Return the current connection object.

        Returns:
            object : active connection object
        """

        return self._connection

    @property
    def target(self) -> str | object:
        """
        Return the current connector target.

        Returns:
            str | object: the target element the connector will connect to
        """

        return self._target

    @target.setter
    def target(self, new_target: str | object) -> None:
        """
        Set the connection target.

        Args:
            new_target (any) : new target of the connector
        """

        self._target = new_target

    @property
    def service_name(self) -> str | None:
        """
        Return the service name the connector will use to store credentials.

        Returns:
            str | None: service name used by the connector
        """

        return self._service_name

    @service_name.setter
    def service_name(self, new_service_name: str, use_credentials: bool) -> None:
        """
        Set the service name bound to the current connector.

        Args:
            new_service_name (str) : new service name for the connector
            use_credentials (bool) : wheither the connector should use credentials
        """

        self._service_name = new_service_name

        if use_credentials:
            self._credentials = CredentialHelper.get_credentials(new_service_name)

    @abstractmethod
    def connect(self, *args: Any, **kwargs: Any) -> None:
        """
        Connect to the target.

        Args:
            *args (tuple)  : any args the overriding method provides
            **kwargs (dict): any kwargs the overriding method provides
        """

        raise NotImplementedError(
            f"{__class__.__name__}.connect::Method must be implemented by the overloading class"
        )

    @abstractmethod
    def search(
        self,
        search_filter: Any,
        attributes: list[str] | None,
        *args: Any,
        **kwargs: Any,
    ) -> list[Any]:
        """
        Retrieve data from the target.

        Args:
            search_filter (Any)   : a way to narrow search scope or search results. It may be a string, a tuple, or even a callback function
            attributes (list[str]): a list of attributes to keep in the search results
            *args (tuple)         : any args the overriding method provides
            **kwargs (dict)       : any kwargs the overriding method provides

        Returns:
            list[any] : list of results
        """

        raise NotImplementedError(
            f"{__class__.__name__}.search::Method must be implemented by the overloading class"
        )
