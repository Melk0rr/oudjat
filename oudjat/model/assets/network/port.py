from enum import Enum
from typing import Dict


class PortState(Enum):
    """State of a port"""

    CLOSED = 0
    OPENED = 1


class Port:
    """Port class"""

    # ****************************************************************
    # Attributes & Constructor

    def __init__(
        self,
        port_number: int = 80,
        application: str = "Unknown",
        state: PortState = PortState.OPENED,
    ):
        """Constructor"""
        if not isinstance(port_number, int):
            raise ValueError(f"Invalid port number: {port_number} !")

        self.number = port_number
        self.application = application
        self.state = state

    # ****************************************************************
    # Methods

    def get_number(self) -> int:
        """Getter for port number"""
        return self.number

    def get_application(self) -> str:
        """Getter for application"""
        return self.application

    def get_state(self) -> PortState:
        """Getter for port open state"""
        return self.state

    def set_number(self, number: int) -> None:
        """Setter for port number"""
        if isinstance(number, int):
            self.number = number

        else:
            raise ValueError(f"Invalid port number: {number} !")

    def set_state(self, new_state: PortState = PortState.OPENED) -> None:
        """Setter for port open state"""
        self.state = new_state

    def __str__(self) -> str:
        """Returns a string based on port number and application"""
        return f"{self.application}({self.number})"

    def to_dictionary(self) -> Dict:
        """Returns a dictionary based on port number and application"""
        return {"number": self.number, "application": self.application}

