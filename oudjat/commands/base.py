class Base(object):
    """A base command."""

    def __init__(self, options, *args, **kwargs):
        """
        Constructor

        Args:
            options (dict): A dictionary of configuration options for the command.
            args (tuple): Positional arguments passed to the constructor.
            kwargs (dict): Keyword arguments passed to the constructor.

        This method initializes the instance variables `options`, `args`, and `kwargs`.
        """

        self.options = options
        self.args = args
        self.kwargs = kwargs

    def run(self) -> None:
        """
        Base run method to be implemented by subclasses.

        Raises:
            NotImplementedError: Indicates that the `run` method must be overridden in any subclass.
        """

        raise NotImplementedError(
            f"{__class__.__name__}.run::Method must be implemented by the overloading class"
        )
