from typing import List, Any

from oudjat.utils.credentials import get_credentials

class Connector:
  """ Base connector """
  def __init__(self, target, service_name, *args, **kwargs):
    """ Constructor """
    self.target = target
    self.service_name = service_name

    self.credentials = get_credentials(self.service_name)

  def connect(self) -> None:
    """ Connects to the target """
    raise NotImplementedError(
      "data() method must be implemented by the overloading class")

  def search(self) -> List[Any]:
    """ Connects to the target """
    raise NotImplementedError(
      "data() method must be implemented by the overloading class")