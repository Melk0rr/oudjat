from enum import Enum

class OSFamily(Enum):
  """ OS family enumeration """
  ANDROID = "android"
  BSD = "bsd"
  LINUX = "linux"
  MAC = "mac"
  UNIX = "unix"
  WINDOWS = {
    "editions": {
      "E"  : [ "Enterprise", "Education", "IoT" ],
      "W"  : [ "Home", "Pro", "Pro Education" ],
      "LTS": "Long Therm Service"
    },

    "software": ["windows", "windowsserver"]
  }

  