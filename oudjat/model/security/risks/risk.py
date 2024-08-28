from typing import List

from oudjat.model.security.risks.risk_measure import RiskMeasure

class Risk:
  """ A class to modelise security risks """

  # ****************************************************************
  # Attributes & Constructors

  risk_table = [
    [ 3, 3, 4, 4 ],
    [ 2, 2, 3, 4 ],
    [ 1, 2, 2, 3 ],
    [ 1, 1, 1, 2 ],
  ]

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

    self.severity = None
    self.value = None
    
  def get_severity(self) -> int:
    """ Getter for the risk score """
    if self.likelihood is None or self.impact is None
      raise ValueError("Risk::You need to set risk likelihood and impact to get its score !")
    
    self.value = self.likelihood.value * self.impact.value
    
    self.severity = self.risk_table[self.impact.value][self.likelihood.value]
    return self.severity
    
  def to_string(self) -> str:
    """ Converts the current instance into a string """
    return f"{self.name}: {self.get_severity().name}"