"""A module to centralize common behavior accross all connectors."""

from abc import ABC, abstractmethod
from typing import Any

from keyring.credentials import SimpleCredential

from oudjat.utils import CredentialHelper


class Connector(ABC):
    """
    A class serves as a base for any type of connector.

    A connector can be seen as a hook to a data source that is used to pull/extract data from it.
    """

    # ****************************************************************
    # Attributes & Constructors

    def __init__(
        self, target: Any, username: str | None = None, password: str | None = None
    ) -> None:
        """
        Create a new instance of Connector.

        Args:
            target (Any)  : Connector target
            username (str): Username to use for the connection
            password (str): Password to use for the connection
        """

        self._target: Any = target

        # Retrieve credentials for the service
        self._credentials: SimpleCredential | None = None
        if username and password:
            self._credentials = SimpleCredential(username, password)

        self._connection: Any = None

    # ****************************************************************
    # Methods

    @property
    def connection(self) -> Any:
        """
        Return the current connection object.

        Returns:
            Any : Active connection object
        """

        return self._connection

    @property
    def target(self) -> Any:
        """
        Return the current connector target.

        Returns:
            Any: The target element the connector will connect to
        """

        return self._target

    @target.setter
    def target(self, new_target: Any) -> None:
        """
        Set the connection target.

        Args:
            new_target (any) : new target of the connector
        """

        self._target = new_target

    def set_creds_from_svc_name(self, svc_name: str) -> None:
        """
        Set the service name bound to the current connector.

        Args:
            svc_name (str): Service name used to retrieve credentials
        """

        self._credentials = CredentialHelper.get_credentials(svc_name)

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
    def fetch(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> list[Any]:
        """
        Retrieve data from the target.

        Args:
            *args (tuple)         : any args the overriding method provides
            **kwargs (dict)       : any kwargs the overriding method provides

        Returns:
            list[any] : list of results
        """

        raise NotImplementedError(
            f"{__class__.__name__}.search::Method must be implemented by the overloading class"
        )
