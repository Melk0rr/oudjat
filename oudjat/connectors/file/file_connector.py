from typing import Any, Dict, List, Union

from oudjat.connectors.connector import Connector
from oudjat.control.data import DataFilter
from oudjat.utils.file import check_path

from .file_types import FileType


class FileConnector(Connector):
    """File connector to interact with different file types"""

    # ****************************************************************
    # Attributes & Constructors

    def __init__(self, path: str, source: str):
        """Constructor for the FileConnector class.

        Args:
            path (str)  : The path to the file.
            source (str): The source identifier or description of the file.
        """

        check_path(path)
        file_ext = path.split(".")[-1]

        self.source = source
        self.filetype = FileType[file_ext.upper()]
        self.import_function = self.filetype.value.get("import")

        self.connection = False
        self.data = None
        super().__init__(path, service_name=None, use_credentials=False)

    # ****************************************************************
    # Methods

    def get_data(self) -> List[Any]:
        """
        Getter for file data.

        Returns:
            List[Any]: The stored data from the file.
        """

        if not self.connection:
            self.connect()

        return self.data

    def set_path(self, new_path: str) -> None:
        """
        Setter for connector path.

        Args:
            new_path (str): The new file path to be set.
        """

        check_path(new_path)
        self.target = new_path

    def connect(self) -> None:
        """
        'Connects' (kind of) to the file and uses the import function to load data.

        Raises:
            NotImplementedError: This method must be implemented by inheriting classes.
        """

        raise NotImplementedError("data() method must be implemented by the overloading class")

    def disconnect(self) -> None:
        """
        'Disconnects' from the targeted file by resetting data and connection status.
        """

        self.data = None
        self.connection = False

    def search(
        self, search_filter: List[Dict], attributes: Union[str, List[str]] = None
    ) -> List[Any]:
        """
        Searches into the imported data based on given filters and attributes.

        Args:
            search_filter (List[Dict])                 : Filters to apply for searching.
            attributes (Union[str, List[str], optional): Specific attributes to retrieve from filtered results.

        Returns:
            List[Any]: The list of elements that match the search criteria.
        """

        if not self.connection:
            self.connect()

        res = []

        for el in self.data:
            conditions = DataFilter.get_conditions(el, filters=search_filter)

            if conditions:
                res.append({k: v} for k, v in el if k in attributes)

        return res


class CSVConnector(FileConnector):
    """Specific file connector for CSV files"""

    # ****************************************************************
    # Attributes & Constructors

    def __init__(self, path: str, source: str, delimiter: str = "|"):
        """
        Constructor for the CSVConnector class.

        Args:
            path (str)               : The path to the CSV file.
            source (str)             : The source identifier or description of the CSV file.
            delimiter (str, optional): Delimiter used in the CSV file. Defaults to "|".

        Raises:
            ValueError: If an invalid delimiter is provided.
        """

        if len(delimiter) > 1:
            raise ("Invalid delimiter provided. Please provide a single character")

        self.delimiter = delimiter
        super().__init__(path, source)

    # ****************************************************************
    # Methods

    def connect(self, callback: object) -> List[Any]:
        """
        Implementation of the parent's 'connect' method specific to CSV files.

        Args:
            callback (object): Callback function for additional processing after file import.

        Returns:
            List[Any]: The list of data imported from the CSV file.

        Raises:
            Exception: If there is an error during the connection process.
        """

        try:
            self.data = self.import_function(
                file_path=self.target, delimiter=self.delimiter, callback=callback
            )
            self.connection = True

        except Exception as e:
            raise (f"CSVConnector::Error connecting to file {self.target}\n{e}")
