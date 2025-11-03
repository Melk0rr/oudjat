"""A module to describe data sources and (in the shadows) bind them to connectors."""

from oudjat.connectors.connector import Connector


class DataSource:
    """A generic class to describe data sources and trace data origin."""

    # ****************************************************************
    # Attributes & Constructors

    def __init__(self, name: str, description: str | None = None) -> None:
        """
        Initialize a new instance of DataSource.

        Args:
            name (str)       : the name of the data source
            description (str): a description for the new data source
        """

        self._name: str = name
        self._description: str | None = description

        self._connectors: dict[str, "Connector"] = {}

    # ****************************************************************
    # Methods

    @property
    def name(self) -> str:
        """
        Return the name of the data source.

        Returns:
            str: current name of the data source
        """

        return self._name

    @property
    def description(self) -> str | None:
        """
        Return the description of the data source.

        Returns:
            str: current description of the data source
        """

        return self._description

    @property
    def connectors(self) -> dict[str, "Connector"]:
        """
        Return the current data source connectors.

        Returns:
            Dict: the connectors attached to this data source
        """

        return self._connectors

    def get_connector(self, connector_key: str) -> "Connector":
        """
        Return one of the data source connector based on its key.

        Args:
            connector_key (str): the key of the desired connector

        Returns:
            Connector: the connector matching the provided key
        """

        if connector_key not in self.connectors:
            raise ValueError(f"{__class__.__name__}.get_connector::Invalid connector key provided")

        return self.connectors[connector_key]

    def add_connector(self, connector_key: str, new_connector: "Connector") -> None:
        """
        Add a new connector to the current data source.

        Args:
            connector_key (str)      : the key to use for the new connector
            new_connector (Connector): the new connector to add
        """

        self.connectors[connector_key] = new_connector

    def delete_connector(self, connector_key: str) -> None:
        """
        Remove one of the connectors of the current data source based on a key.

        Args:
            connector_key (str): key of the connector to delete
        """

        del self.connectors[connector_key]

    def clear_connectors(self) -> None:
        """Clear the connectors of the data source."""

        del self._connectors
        self._connectors = {}

