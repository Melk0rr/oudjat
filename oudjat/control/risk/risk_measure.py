from enum import IntEnum


class RiskMeasure(IntEnum):
    """An enumeration to handle risk measures (likelihood and impact)"""
    MINOR = 1
    MODERATE = 2
    HIGH = 3
    CRITICAL = 4

