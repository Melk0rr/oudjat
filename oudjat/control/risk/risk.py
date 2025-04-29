from typing import Union

from .risk_measure import RiskMeasure


class Risk:
    """A class to modelise security risks"""

    # ****************************************************************
    # Attributes & Constructors

    # Risk 2D table
    risk_table = [
        [1, 1, 1, 2],
        [1, 2, 2, 3],
        [2, 2, 3, 4],
        [3, 3, 4, 4],
    ]

    def __init__(
        self,
        risk_id: str,
        name: str,
        description: str,
        likelihood: Union[RiskMeasure, int] = None,
        impact: Union[RiskMeasure, int] = None,
    ):
        """
        Returns a new instance of Risk

        Args:
            risk_id (str)                 : the id used to identify the new risk
            name (str)                    : name of the new risk
            description (str)             : string to describe the new risk
            likelihood (int | RiskMeasure): the probability that the risk will happen (value between 1 and 4)
            impact (int | RiskMeasure)    : the impact if the risk is concretized (value between 1 and 4)
        """

        self.id = risk_id
        self.name = name
        self.description = description

        # Handle risk parameters type
        if isinstance(likelihood, int):
            likelihood = RiskMeasure(min(max(1, likelihood), 4))

        if isinstance(impact, int):
            impact = RiskMeasure(min(max(1, impact), 4))

        self.likelihood = likelihood
        self.impact = impact

        self.severity = None
        self.value = None

    # ****************************************************************
    # Methods

    def get_severity(self) -> int:
        """
        Getter for the risk score

        Returns:
            int: severity of the risk (value between 1 and 16)
        """

        if self.likelihood is None or self.impact is None:
            raise ValueError(f"{__class__.__name__}.get_severity::You need to set risk likelihood and impact to get its score !")

        self.value = self.likelihood * self.impact

        base_severity = self.risk_table[self.impact - 1][self.likelihood - 1]
        self.severity = RiskMeasure(base_severity)

        return self.severity

    def set_likelihood(self, likelihood: Union[int, RiskMeasure]) -> None:
        """
        Change the likelihood of the current risk

        Args:
            likelihood (int | RiskMeasure): new likelihood value
        """

        if isinstance(likelihood, int):
            likelihood = RiskMeasure(min(max(1, likelihood), 4))

        self.likelihood = likelihood

    def set_impact(self, impact: Union[int, RiskMeasure]) -> None:
        """
        Change the impact of the current risk

        Args:
            impact (int | RiskMeasure): new impact value
        """

        if isinstance(impact, int):
            impact = min(max(1, impact), 4)
            impact = RiskMeasure(impact)

        self.impact = impact

    def __str__(self) -> str:
        """
        Converts the current instance into a string

        Returns:
            str: a string representation of the current risk containing its name, severity name and value
        """

        return f"{self.name} => {self.get_severity().name} : {self.value}"

    # ****************************************************************
    # Static methods
