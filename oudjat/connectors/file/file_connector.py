"""A module to perform connection to various types of file."""

from typing import Any, Callable, List, Union

from oudjat.connectors.connector import Connector
from oudjat.utils.file_utils import FileHandler, FileType


class FileConnector(Connector):
    """File connector to interact with different file types."""

    # ****************************************************************
    # Attributes & Constructors

    def __init__(self, path: str, source: str) -> None:
        """
        Create a new instance of FileConnector.

        Args:
            path (str)  : The path to the file.
            source (str): The source identifier or description of the file.
        """

        FileHandler.check_path(path)
        file_ext = path.split(".")[-1]

        self.source = source
        try:
            self.filetype = FileType[file_ext.upper()]

        except ValueError:
            raise (
                f"{__class__.__name__}.__init__::{file_ext.upper()} files are not supported by {__class__.__name__}"
            )

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

        FileHandler.check_path(new_path)
        self.target = new_path

    def connect(self, callback: Callable) -> List[Any]:
        """
        'Connect' to the file and import data from it.

        Args:
            callback (object): Callback function for additional processing after file import.

        Returns:
            List[Any]: The list of data imported from the file.

        Raises:
            Exception: if the file does not exist, can't be reached or if there is any error while importing its data
        """

        try:
            self.data = self.filetype.f_import(
                file_path=self.target, delimiter=self.delimiter, callback=callback
            )
            self.connection = True

        except Exception as e:
            raise (f"{__class__.__name__}.connect::Error connecting to file {self.target}\n{e}")

    def disconnect(self) -> None:
        """
        'Disconnects' from the targeted file by resetting data and connection status.
        """

        self.data = None
        self.connection = False

    def search(
        self,
        search_filter_cb: Callable,
        attributes: Union[str, List[str]] = None,
    ) -> List[Any]:
        """
        Search into the imported data based on given filters and attributes.

        Args:
            search_filter_cb (Callable)                : A callback function that provides a predicate
            attributes (Union[str, List[str], optional): Specific attributes to retrieve from filtered results.

        Returns:
            List[Any]: The list of elements that match the search criteria.
        """

        if not self.connection:
            self.connect()

        return [
            {k: v for k, v in el.items() if k in attributes}
            for el in self.data
            if search_filter_cb(el)
        ]

