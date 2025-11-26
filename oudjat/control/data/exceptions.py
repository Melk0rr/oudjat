"""
A helper module to define data control exceptions.
"""


class DecisionTreeBuildError(ValueError):
    """
    A helper class to handle error occuring while building a DecisionTree.
    """

    def __init__(self, message: str) -> None:
        """
        Create a new instance of DecisionTreeBuildError.

        Args:
            message (str): Error message
        """

        self.message: str = message
        super().__init__(self.message)


class DecisionTreeInvalidNodeError(ValueError):
    """
    A helper class to handle invalid DecisionTree node errors.
    """

    def __init__(self, message: str) -> None:
        """
        Create a new instance of DecisionInvalidNodeError.

        Args:
            message (str): Error message
        """

        self.message: str = message
        super().__init__(self.message)


class DataFilterInvalidOperatorError(ValueError):
    """
    A helper class to handle invalid DataFilter operator errors.
    """

    def __init__(self, message: str) -> None:
        """
        Create a new instance of DataFilterInvalidOperatorError.

        Args:
            message (str): Error message
        """

        self.message: str = message
        super().__init__(self.message)


class DataSourceConnectorKeyError(ValueError):
    """
    A helper class to handle invalid DataSource connector key errors.
    """

    def __init__(self, message: str) -> None:
        """
        Create a new instance of DataSourceConnectorKeyError.

        Args:
            message (str): Error message
        """

        self.message: str = message
        super().__init__(self.message)

class DataSetPerimeterError(ValueError):
    """
    A helper class to handle DataSet perimeter errors.
    """

    def __init__(self, message: str) -> None:
        """
        Create a new instance of DataSetPerimeterError.

        Args:
            message (str): Error message
        """

        self.message: str = message
        super().__init__(self.message)
