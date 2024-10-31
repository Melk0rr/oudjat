from enum import Enum

from oudjat.model.assets.computer import ComputerType
from . import Windows, WindowsServer

class OSOption(Enum):
  """ Agregation of oses """
  WINDOWS = {
    "class": Windows
  }
  WINDOWSSERVER = {
    "class": WindowsServer
  }