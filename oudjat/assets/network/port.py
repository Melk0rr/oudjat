"""A module that describe TCP/UDP ports."""

from enum import IntEnum
from typing import override


class PortState(IntEnum):
    """State of a port."""

    CLOSED = 0
    OPENED = 1


class Port:
    """A class to handle TCP/UDP ports."""

    # ****************************************************************
    # Attributes & Constructor

    def __init__(
        self,
        port_number: int = 80,
        application: str = "Unknown",
        state: PortState = PortState.OPENED,
    ) -> None:
        """
        Create a new instance of Port.

        Args:
            port_number (int): the number of the port. Default is 80.
            application (str): the name of the application using the port. Default is "Unknown".
            state (PortState): the current state of the port. Default is PortState.OPENED.

        Raises:
            ValueError: If the provided `port_number` is not an integer.
        """

        self._number: int = port_number
        self._application: str = application
        self._state: PortState = state

    # ****************************************************************
    # Methods

    @property
    def number(self) -> int:
        """
        Return the number of the current port.

        Returns:
            int: number associated with this port instance
        """

        return self._number

    @number.setter
    def number(self, new_port_number: int) -> None:
        """
        Change the current port number based on the provided value.

        Args:
            new_port_number (int): new port number that will be associated with this instance
        """

        self._number = new_port_number

    @property
    def application(self) -> str:
        """
        Return the application that listens on this port.

        Returns:
            str: the application behind the port
        """

        return self._application

    @application.setter
    def application(self, new_application: str) -> None:
        """
        Change the application bound to this port.

        Args:
            new_application (str): new application listening on this port
        """

        self._application = new_application

    @property
    def state(self) -> PortState:
        """
        Return the current state of the port.

        Returns:
            PortState: state of the port as a PortState enum object (OPENED or CLOSED)

        Example:
            exemple_port = Port(42)
            print(exemple_port.state) -> OPENED
        """

        return self._state

    @state.setter
    def state(self, new_state: PortState = PortState.OPENED) -> None:
        """
        Set the state of the current port.

        Args:
            new_state (PortState): new state of the port

        Example:
            exemple_port = Port(42)
            print(exemple_port.state) -> OPENED

            exemple_port.state = PortState.CLOSED
            print(exemple_port.state) -> CLOSED
        """

        self._state = new_state

    def __int__(self) -> int:
        """
        Convert the current instance into an integer.

        Returns:
            int: current port instance as an integer

        Example:
            http_port = Port(80, "HTTP")
            print(int(http_port)) -> 80
        """

        return self.number

    @override
    def __str__(self) -> str:
        """
        Return a string based on port number and application.

        Returns:
            str: A formatted string showing the port number and application name.
        """

        return f"{self.application}({self.number})"

    def to_dict(self) -> dict:
        """
        Return a dictionary based on port number and application.

        Returns:
            Dict: A dictionary containing the port number and application name.
        """

        return {"number": self.number, "application": self.application, "status": self.state.name}
