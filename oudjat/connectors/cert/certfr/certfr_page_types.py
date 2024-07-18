from enum import Enum

class CERTFRPageTypes(Enum):
  """ Enumeration describing possible CERTFR page types """
  ALE = "alerte"
  AVI = "avis"
  CTI = "cti"
  IOC = "ioc"
  DUR = "dur"