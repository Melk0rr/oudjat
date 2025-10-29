"""
A module that handles SCCM server connection and interractions.
"""

from typing import Any, override

import pyodbc

from oudjat.utils.credentials import NoCredentialsError
from oudjat.utils.types import StrType

from ...connector import Connector
from .odbc_drivers import ODBCDriver


class SCCMConnector(Connector):
    """
    A class that allows for SCCM interactions through SQL server conenction.
    """

    # ****************************************************************
    # Attributes & Constructors

    def __init__(
        self,
        server: str,
        db_name: str,
        username: str | None = None,
        password: str | None = None,
        driver: ODBCDriver = ODBCDriver.SQL_SERVER,
        port: int = 1433,
        trusted_connection: bool = False,
    ) -> None:
        """
        Create a new SCCMServer instance.

        Args:
            server (str)             : The name of the SQL server to connect to
            db_name (str)            : The name of the database to interact with
            username (str)           : Username to use for the connection
            password (str)           : Password to use for the connection
            driver (ODBCDriver)      : The ODBC driver to use for the connection
            port (int)               : The port to request to
            trusted_connection (bool): Whether to use MS Windows authentication or not
            service_name (str)       : Service name used to register credentials if trusted_connection is false
        """

        super().__init__(target=server, username=username, password=password)

        self._trusted_connection: bool = trusted_connection

        self._driver: "ODBCDriver" = driver
        self._port: int = port
        self._database: str = db_name

        self._connection: pyodbc.Connection
        self._cursor: pyodbc.Cursor

    # ****************************************************************
    # Methods

    @property
    def driver(self) -> "ODBCDriver":
        """
        Return the driver used by the current SCCM connector for the SQL Server connection.

        Returns:
            ODBCDriver: ODBC driver currently in use
        """

        return self._driver

    @driver.setter
    def driver(self, new_driver: "ODBCDriver") -> None:
        """
        Set a new driver to be used by the current connector.

        Args:
            new_driver (ODBCDriver): new driver value
        """

        self._driver = new_driver

    @override
    def connect(self) -> None:
        """
        Connect to the target server.
        """

        if not self._trusted_connection and self._credentials is None:
            raise NoCredentialsError(
                f"{__class__.__name__}.__init__::",
                "Trusted connection is set to False, but no credentials where provided",
                self._target
            )

        try:
            cnx_creds_args: dict[str, str] = {}
            if not self._trusted_connection and self._credentials:
                cnx_creds_args = {
                    "uid": self._credentials.username,
                    "pwd": self._credentials.password,
                }

            self._connection = pyodbc.connect(
                driver=self._driver.value,
                server=self._target,
                port=self._port,
                database=self._database,
                trusted_connection=self._trusted_connection,
                **cnx_creds_args,
            )

            self._cursor = self._connection.cursor()

        except ConnectionError as e:
            raise ConnectionError(
                f"An error occured while trying to connect to {self._target}::{self._database}: \n{e}"
            )

    @override
    def fetch(
        self,
        search_filter: str,
        attributes: StrType | None = None,
    ) -> list[dict[str, Any]]:
        """
        Perform a request to the SQL server.

        Detailed description.

        Args:
            search_filter (str): A way to narrow search scope or search results. It may be a string, a tuple, or even a callback function
            attributes (StrType | None): A list of attributes to keep in the search results

        Returns:
            list[Any]: list of found element based on provided search filter
        """

        try:
            _ = self._cursor.execute(search_filter)

        except Exception as e:
            raise Exception(
                f"An error occured while searching in {self._target}::{self._database}: \n{e}"
            )

        res_columns: list[str] = [column[0] for column in self._cursor.description]
        return [dict(zip(res_columns, row)) for row in self._cursor.fetchall()]
