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

        self.number: int = port_number
        self.application: str = application
        self.state: PortState = state

    # ****************************************************************
    # Methods

    def get_number(self) -> int:
        """
        Getter for port number.

        Returns:
            int: The number of the port.
        """

        return self.number

    def get_application(self) -> str:
        """
        Getter for application.

        Returns:
            str: The name of the application using the port.
        """

        return self.application

    def get_state(self) -> PortState:
        """
        Getter for port open state.

        Returns:
            PortState: The current state of the port.
        """

        return self.state

    def set_number(self, number: int) -> None:
        """
        Setter for port number.

        Args:
            number (int): The new number for the port.

        Raises:
            ValueError: If the provided `number` is not an integer.
        """

        self.number = number

    def set_state(self, new_state: PortState = PortState.OPENED) -> None:
        """
        Setter for port open state.

        Args:
            new_state (PortState): The new state for the port. Default is PortState.OPENED.
        """

        self.state = new_state

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

        return {
            "number": self.number,
            "application": self.application,
            "status": self.state.name
        }
