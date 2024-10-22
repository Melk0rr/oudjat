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
    "software": ["windows", "windowsserver"]
  }

  