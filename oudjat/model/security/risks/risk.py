from typing import Union

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
    likelihood: Union[RiskMeasure, int] = None,
    impact: Union[RiskMeasure, int] = None
  ):
    """ Constructor """

    self.id = id
    self.name = name
    self.description = description

    # Handle risk parameters type
    if isinstance(likelihood, int):
      likelihood = min(max(1, likelihood), 4)
      likelihood = RiskMeasure(likelihood)
      
    if isinstance(impact, int):
      impact = min(max(1, impact), 4)
      impact = RiskMeasure(impact)
    
    self.likelihood = likelihood
    self.impact = impact

    self.severity = None
    self.value = None
    
  def get_severity(self) -> int:
    """ Getter for the risk score """
    if self.likelihood is None or self.impact is None:
      raise ValueError("Risk::You need to set risk likelihood and impact to get its score !")
    
    self.value = self.likelihood.value * self.impact.value
    
    base_severity = self.risk_table[self.impact.value - 1][self.likelihood.value - 1]
    self.severity = RiskMeasure(base_severity)
    
    return self.severity

  def set_likelihood(self, likelihood: Union[RiskMeasure, int]) -> None:
    """ Setter for risk impact """

    if isinstance(likelihood, int):
      likelihood = min(max(1, likelihood), 4)
      likelihood = RiskMeasure(likelihood)

    self.likelihood = likelihood

  def set_impact(self, impact: Union[RiskMeasure, int]) -> None:
    """ Setter for risk impact """

    if isinstance(impact, int):
      impact = min(max(1, impact), 4)
      impact = RiskMeasure(impact)

    self.impact = impact
    
  def to_string(self) -> str:
    """ Converts the current instance into a string """
    return f"{self.name} => {self.get_severity().name} : {self.value}"