from enum import Enum

class WindowsEdition(Enum):
  """ Windows edition enum """
  E   = [ "Enterprise", "Education", "IOT Enterprise" ]
  W   = [ "Home", "Pro", "Pro Education" ]
  IOT = [ "IOT" ]

class OSFamily(Enum):
  """ OS family enumeration """
  ANDROID = "android"
  BSD = "bsd"
  LINUX = "linux"
  MAC = "mac"
  UNIX = "unix"
  WINDOWS = {
    "editions": WindowsEdition,
    "os": [
      {
        "id": "windows",
        "name": "Windows",
        "label": "ms-windows"
      },
      {
        "id": "windowsserver",
        "name": "Windows Server",
        "label": "ms-windows"
      }
    ]
  }

