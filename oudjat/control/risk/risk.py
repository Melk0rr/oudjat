"""A module to describe the notion of risk."""

from typing import override

from .risk_measure import RiskMeasure


class Risk:
    """A class to modelise security risks."""

    # ****************************************************************
    # Attributes & Constructors

    # Risk 2D table
    risk_table: list[list[int]] = [
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
        likelihood: RiskMeasure | int = 0,
        impact: RiskMeasure | int = 0,
    ):
        """
        Return a new instance of Risk.

        Args:
            risk_id (str)                 : the id used to identify the new risk
            name (str)                    : name of the new risk
            description (str)             : string to describe the new risk
            likelihood (int | RiskMeasure): the probability that the risk will happen (value between 1 and 4)
            impact (int | RiskMeasure)    : the impact if the risk is concretized (value between 1 and 4)
        """

        self._id: str = risk_id
        self.name: str = name
        self.description: str = description

        self.likelihood: RiskMeasure = RiskMeasure(likelihood)
        self.impact: RiskMeasure = RiskMeasure(impact)

        self.severity = None
        self.value = None

    # ****************************************************************
    # Methods

    def get_id(self) -> str:
        """
        Return the risk ID.

        Returns:
            str: unique id of the current risk
        """

        return self._id

    def get_severity(self) -> RiskMeasure:
        """
        Getter for the risk score.

        Returns:
            int: severity of the risk (value between 1 and 16)
        """

        self.value = self.likelihood * self.impact

        base_severity = self.risk_table[self.impact - 1][self.likelihood - 1]
        self.severity = RiskMeasure(base_severity)

        return self.severity

    def set_likelihood(self, likelihood: int | RiskMeasure) -> None:
        """
        Change the likelihood of the current risk.

        Args:
            likelihood (int | RiskMeasure): new likelihood value
        """

        self.likelihood = RiskMeasure(min(max(1, likelihood), 4))

    def set_impact(self, impact: int | RiskMeasure) -> None:
        """
        Change the impact of the current risk.

        Args:
            impact (int | RiskMeasure): new impact value
        """

        self.impact = RiskMeasure(min(max(1, impact), 4))

    @override
    def __str__(self) -> str:
        """
        Convert the current instance into a string.

        Returns:
            str: a string representation of the current risk containing its name, severity name and value
        """

        return f"{self.name} => {self.get_severity().name} : {self.value}"

    # ****************************************************************
    # Static methods
