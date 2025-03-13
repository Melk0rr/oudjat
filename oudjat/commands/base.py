
class Base(object):
  """A base command."""

  def __init__(self, options, *args, **kwargs):
    self.options = options
    self.args = args
    self.kwargs = kwargs

  def run(self) -> None:
    """ Base run method to be implemented by subclasses """
    raise NotImplementedError(
        "run() method must be implemented by the overloading class")
