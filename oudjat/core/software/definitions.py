"""
A module to define package wide utilities.
"""

STAGE_REG: str = r"((?:a|b|r|rc|sp)(?:\d*)?)"
VERSION_REG: str = rf"(\d+)(?:\.(\d+))?(?:\.(\d+))?{STAGE_REG}?"

