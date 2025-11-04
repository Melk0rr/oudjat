"""A module to perform connection to various types of file."""

from typing import Any, Callable, override

from oudjat.connectors.connector import Connector
from oudjat.utils.file_utils import FileUtils, FileType


class FileConnector(Connector):
    """File connector to interact with different file types."""

    # ****************************************************************
    # Attributes & Constructors

    def __init__(self, file: str, source: str) -> None:
        """
        Create a new instance of FileConnector.

        Args:
            file (str)  : The path to the file.
            source (str): The source identifier or description of the file.
        """

        if not FileUtils.check_path(file):
            raise FileExistsError(
                f"{__class__.__name__}.__init__::Invalid file path provided: {file}"
            )

        file_ext: str = file.split(".")[-1]

        self._source: str = source
        try:
            self._filetype: FileType = FileType[file_ext.upper()]

        except ValueError:
            raise ValueError(
                f"{__class__.__name__}.__init__::{file_ext.upper()} files are not supported by {__class__.__name__}"
            )

        self._connection: bool = False
        self._data: list[Any] | None = None

        super().__init__(file)

    # ****************************************************************
    # Methods

    @property
    def data(self) -> list[Any] | None:
        """
        Getter for file data.

        Returns:
            list[Any]: The stored data from the file.
        """

        if not self.connection:
            self.connect()

        return self._data

    @Connector.target.setter
    @override
    def target(self, new_target: Any) -> None:
        """
        Setter for connector path.

        Args:
            new_target (str): The new file path to be set.
        """

        if not isinstance(new_target, str):
            raise ValueError(f"{__class__.__name__}.check_path::Please provide a string")

        if not FileUtils.check_path(new_target):
            raise FileExistsError(
                f"{__class__.__name__}.check_path::Invalid file path provided: {new_target}"
            )

        super()._target = new_target

    @override
    def connect(self, payload: dict[str, Any] | None = None) -> None:
        """
        'Connect' to the file and import data from it.

        Args:
            payload (dict[str, Any] | None): Additional options to pass to the file import function

        Raises:
            FileExistsError: if the file does not exist, can't be reached or if there is any error while importing its data
        """

        if payload is None:
            payload = {}

        try:
            self._data = self._filetype.f_import(file_path=self._target, **payload)
            self._connection = True

        except FileExistsError as e:
            raise FileExistsError(
                f"{__class__.__name__}.connect::Error connecting to file {self.target}\n{e}"
            )

    def disconnect(self) -> None:
        """
        'Disconnects' from the targeted file by resetting data and connection status.
        """

        self._data = None
        self._connection = False

    @override
    def fetch(
        self,
        search_filter: Callable[..., bool],
        attributes: list[str] | None = None,
        payload: dict[str, Any] | None = None
    ) -> list[Any]:
        """
        Search into the imported data based on given filters and attributes.

        Args:
            search_filter (Callable)        : A callback function that provides a predicate
            attributes (list[str], optional): Specific attributes to retrieve from filtered results.
            payload (dict[str, Any] | None): Additional options to pass to the file import function

        Returns:
            list[Any]: Data retrived from the file based on provided filters
        """

        if not self.connection:
            self.connect(payload=(payload or {}))

        if self.data is None:
            return []

        return [
            {k: v for k, v in el.items() if k in attributes}
            for el in self.data
            if search_filter(el)
        ]
