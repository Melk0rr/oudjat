from typing import List

from oudjat.model.security.risks.risk_measure import RiskMeasure

class Risk:
  """ A class to modelise security risks """

  # ****************************************************************
  # Attributes & Constructors
  def __init__(
    self,
    id: str,
    name: str,
    description: str,
    likelihood: RiskMeasure = None,
    impact: RiskMeasure = None
  ):
    """ Constructor """

    self.id = id
    self.name = name
    self.description = description

    self.likelihood = likelihood
    self.impact = impact

    self.score = None
    
  
    
  