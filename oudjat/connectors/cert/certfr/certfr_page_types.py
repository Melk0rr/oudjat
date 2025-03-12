from enum import Enum


class CERTFRPageType(Enum):
    """Enumeration describing possible CERTFR page types"""

    ALE = "alerte"
    AVI = "avis"
    CTI = "cti"
    IOC = "ioc"
    DUR = "dur"

