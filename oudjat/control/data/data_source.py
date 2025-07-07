"""A module to describe data sources and (in the shadows) bind them to connectors."""

from typing import Dict

from oudjat.connectors.connector import Connector


class DataSource:
    """A generic class to describe data sources and trace data origin."""

    # ****************************************************************
    # Attributes & Constructors

    def __init__(
        self,
        name: str,
        data_source_type: str = None,
        description: str = None,
        connectors: Dict[str, Connector] = None,
    ) -> None:
        """
        Initialize a new instance of DataSource.

        Args:
            name (str)            : the name of the data source
            data_source_type (str): a string that may help to classify the data source
            description (str)     : a description for the new data source
            connectors (Dict)     : dictionary of connectors to assign to the data source
        """

        self.name = name
        self.description = description
        self.type = data_source_type

        self.connectors: Dict[str, Connector] = {}

        if connectors is not None:
            self.set_connectors(connectors)

    # ****************************************************************
    # Methods

    def get_name(self) -> str:
        """
        Return the name of the data source.

        Returns:
            str: current name of the data source
        """

        return self.name

    def get_description(self) -> str:
        """
        Return the description of the data source.

        Returns:
            str: current description of the data source
        """

        return self.description

    def get_connectors(self) -> Dict:
        """
        Return the current data source connectors.

        Returns:
            Dict: the connectors attached to this data source
        """

        return self.connectors

    def get_connector(self, connector_key: str = None) -> "Connector":
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

    def set_connectors(self, connectors: Dict[str, Connector]) -> None:
        """
        Set the connectors of the current data source.

        A dictionary of connectors must be provided in parameter.

        Args:
            connectors (Dict): a dictionary of connectors with string keys
        """

        if not isinstance(connectors, Dict):
            raise ValueError(f"{__class__.__name__}.set_connectors::Invalid connectors provided")

        self.connectors = connectors

    def add_connector(self, connector_key: str, new_connector: "Connector") -> None:
        """
        Add a new connector to the current data source.

        Args:
            connector_key (str)      : the key to use for the new connector
            new_connector (Connector): the new connector to add
        """

        if not isinstance(new_connector, Connector):
            raise ValueError(
                f"{__class__.__name__}.add_connector::Invalid new connector provided. Please provide a valid Connector instance"
            )

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

        del self.connectors
        self.connectors = {}

    def connect(self, connection_opts: Dict[str, Dict]) -> bool:
        """
        Initiate the connection for current data source connectors based on the provided parameters.

        The method uses the provided connection options to initiate connection to the current data source connectors through their connect method.
        Each key of the connection options must match one connector key of the current data source.
        With each key, comes a parameter dictionary passed to the connector connect method.

        You can specify one, multiple or all connectors of the source.
        If one connector's key is not in the connection options, the connection will not be initialized for this connector.

        Args:
            connection_opts (Dict): a dictionary of connection options.

        Returns:
            bool: True if no error occured in the process. False otherwise.

        Example:
            connectors = {
                "api": MyCompanyAVAPIConnector(...),
                "file": FileConnector(...)
            }
            my_source = DataSource(name="my_company_antivirus", connectors=connectors)
            my_source.connect(connection_opts={ "api": { whatever_option="", ... } })
        """

        res = True
        try:
            for connector_key, connect_params in connection_opts.items():
                if connector_key not in self.connectors.keys():
                    continue

                if not isinstance(connect_params, dict):
                    raise ValueError(
                        "You must provide a dicitonary for each connector key in your connection options!"
                    )

                self.get_connector(connector_key).connect(**connect_params)

        except Exception as e:
            res = False
            raise f"{__class__.__name__}.connect::{e}"

        return res
