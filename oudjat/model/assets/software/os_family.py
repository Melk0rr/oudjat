from enum import Enum

class OSFamily(Enum):
  """ OS family enumeration """
  ANDROID = "android"
  BSD = "bsd"
  LINUX = "linux"
  MAC = "mac"
  UNIX = "unix"
  WINDOWS = "windows"