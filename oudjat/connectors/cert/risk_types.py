from enum import Enum

class RiskTypes(Enum):
  """ Enumeration describing possible risk values """
  N_A = "Not specified"
  EOP = "Elevation Of Privilege"
  RCE = "Remote Code Execution"
  DOS = "Denial of Service"
  SFB = "Security Bypass"
  IDT = "Identity Theft"
  ID = "Information Disclosure"
  TMP = "Integrity Violation"
  XSS = "Code Injection"