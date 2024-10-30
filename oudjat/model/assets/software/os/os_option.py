from enum import Enum

from . import Windows, WindowsServer

class OSOption(Enum):
  """ Agregation of oses """
  WINDOWS = Windows
  WINDOWSSERVER = WindowsServer