
"""
A helper module to define commands exceptions.
"""

class ConnectorCommandInvalidBackend(ValueError):
    """
    A helper error class to handle invalid connector command backend.
    """

    def __init__(self, message: str) -> None:
        """
        Create a new instance of ConnectorCommandInvalidBackend.

        Args:
            message (str): Error message
        """

        self.message: str = message
        super().__init__(self.message)

