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
        self._name: str = name
        self._description: str = description

        self._likelihood: RiskMeasure = RiskMeasure(min(max(1, likelihood), 4))
        self._impact: RiskMeasure = RiskMeasure(min(max(1, impact), 4))

    # ****************************************************************
    # Methods

    @property
    def id(self) -> str:
        """
        Return the risk ID.

        Returns:
            str: unique id of the current risk
        """

        return self._id

    @property
    def likelihood(self) -> RiskMeasure:
        """
        Return the likelihood of the risk.

        Returns:
            RiskMeasure: a value between 1 and 4 to represent the risk likelihood
        """
        return self._likelihood

    @likelihood.setter
    def likelihood(self, new_likelihood: RiskMeasure) -> None:
        """
        Change the likelihood of the current risk.

        Args:
            new_likelihood (int | RiskMeasure): new likelihood value
        """

        self._likelihood = new_likelihood

    @property
    def impact(self) -> RiskMeasure:
        """
        Return the impact of the risk.

        Returns:
            RiskMeasure: a value between 1 and 4 to represent the risk impact
        """

        return self._impact

    @impact.setter
    def impact(self, new_impact: RiskMeasure) -> None:
        """
        Change the impact of the current risk.

        Args:
            new_impact (int | RiskMeasure): new impact value
        """

        self._impact = RiskMeasure(min(max(1, new_impact), 4))


    @property
    def value(self) -> int:
        """
        Return the value of the current risk based on its likelihood and impact.

        Returns:
            int: a value between 1 and 16 based on the risk likelihood and impact
        """

        return self._likelihood * self._impact

    @property
    def severity(self) -> RiskMeasure:
        """
        Getter for the risk score.

        Returns:
            int: severity of the risk (value between 1 and 16)
        """

        return RiskMeasure(self.risk_table[self.impact - 1][self.likelihood - 1])

    @override
    def __str__(self) -> str:
        """
        Convert the current instance into a string.

        Returns:
            str: a string representation of the current risk containing its name, severity name and value
        """

        return f"{self._name} => {self.severity.name} : {self.value}"

    def to_dict(self) -> dict[str, str | int | RiskMeasure]:
        """
        Convert the current Risk instance into a dictionary.

        Returns:
            dict[str, str | int | RiskMeasure]: a dictionary representing the current instance
        """

        return {
            "id": self._id,
            "name": self._name,
            "description": self._description,
            "likelihood": self._likelihood,
            "impact": self._impact,
            "value": self.value,
            "severity": self.severity
        }

    # ****************************************************************
    # Static methods
