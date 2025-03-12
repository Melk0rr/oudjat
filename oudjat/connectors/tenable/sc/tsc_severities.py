from enum import Enum


class TenableSCSeverity(Enum):
    """Tenable SC severities enumeration"""
    CRITICAL = 4
    HIGH = 3
    MEDIUM = 2
    LOW = 1
    INFO = 0
