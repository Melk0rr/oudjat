from enum import Enum

class RiskTypes(Enum):
  """ Enumeration describing possible risk values """
  N_A = { "en": "Not specified", "fr": "Non spécifié" }
  EOP = { "en": "Elevation Of Privilege", "fr": "Élévation de privilèges" }
  RCE = { "en": "Remote Code Execution", "fr": "Exécution de code arbitraire à distance" }
  DOS = { "en": "Denial of Service", "fr": "Déni de service" }
  SFB = { "en": "Security Bypass", "fr": "Contournement de la politique de sécurité" }
  IDT = { "en": "Identity Theft", "fr": "Usurpation d'identité" }
  ID  = { "en": "Information Disclosure", "fr": "Atteinte à la confidentialité des données" }
  TMP = { "en": "Integrity Violation", "fr": "Atteinte à l'intégrité des données" }
  XSS = { "en": "Code Injection", "fr": "Exécution de code arbitraire" }
  