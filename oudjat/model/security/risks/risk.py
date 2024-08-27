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
    self.score_value = None
    
  def get_score(self) -> int:
    """ Getter for the risk score """
    if self.likelihood is None or self.impact is None
      raise ValueError("Risk::You need to set risk likelihood and impact to get its score !")
    
    self.score_value = self.likelihood.value * self.impact.value
    self.score = RiskMeasure(score_value / 4 + 1)
    return self.score_value
    
    
  