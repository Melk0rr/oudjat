"""A module to handle KPI comparisons."""

from enum import Enum
from typing import Any, Callable, NamedTuple, override

from oudjat.utils import ColorPrint

from .kpi import KPI


class KPIComparatorTendencyProps(NamedTuple):
    """
    A helper class to properly handle KPIComparatorTendency property types.

    Attributes:
        icon (str)                          : the icon that represents the tendency
        print_function (Callable[..., None]): the print function used to display the tendency
    """

    icon: str
    print_function: Callable[..., None]


class KPIComparatorTendency(Enum):
    """
    An enumeration of possible tendencies for a KPIComparator.

    A KPIComparator computes a tendency based on the KPI it compares.
    This tendency describes how a KPI value changed between 2 KPIs (increased, decreased or equal).
    """

    INC = KPIComparatorTendencyProps(icon="", print_function=ColorPrint.green)
    DEC = KPIComparatorTendencyProps(icon="", print_function=ColorPrint.red)
    EQ = KPIComparatorTendencyProps(icon="", print_function=ColorPrint.yellow)

    @property
    def icon(self) -> str:
        """
        Return the icon of the tendency.

        Returns:
            str: icon that represent the tendency
        """
        return self._value_.icon

    @property
    def print_function(self) -> Callable[..., None]:
        """
        Return the print function used to print a KPIComparator result.

        Returns:
            Callable[..., None]: print function used to display a KPIComparator result
        """

        return self._value_.print_function


class KPIComparator:
    """A class to compare the results of 2 KPIs."""

    # ****************************************************************
    # Attributes & Constructors

    def __init__(self, kpi_a: "KPI", kpi_b: "KPI", dont_sort_by_date: bool = False) -> None:
        """
        Return a new instance of KPIComparator.

        Args:
            kpi_a (KPI)             : the first KPI object to compare.
            kpi_b (KPI)             : the second KPI object to compare.
            dont_sort_by_date (bool): whether to use the KPI dates to order them.

        Raises:
            ValueError: If the provided KPIs do not share the same perimeter.
        """

        if kpi_a.perimeter != kpi_b.perimeter:
            raise ValueError(
                f"{__class__.__name__}::Provided KPIs do not share the same perimeter !"
            )

        self._kpis: tuple["KPI", "KPI"] = (
            KPIComparator.kpi_tuple_by_date(kpi_a, kpi_b)
            if not dont_sort_by_date
            else (kpi_a, kpi_b)
        )

        self._tendency: "KPIComparatorTendency"

    # ****************************************************************
    # Methods

    @property
    def kpis(self) -> tuple["KPI", "KPI"]:
        """
        Getter for the KPIs being compared.

        Returns:
            tuple[float, float]: A tuple containing the values of the two KPIs.
        """

        return self._kpis

    @property
    def tendency(self) -> "KPIComparatorTendency":
        """
        Getter for the comparator tendency.

        Returns:
            KPIComparatorTendency: The current tendency represented as a dictionary with keys "icon" and "print".
        """

        return (
            KPIComparatorTendency.INC
            if self._kpis[0].value < self._kpis[1].value
            else KPIComparatorTendency.DEC
            if self._kpis[0].value > self._kpis[1].value
            else KPIComparatorTendency.EQ
        )

    def compare(self) -> None:
        """
        Compare the values of the KPIs and set the tendency.

        This method compares the stored values of the KPIs, determines the tendency using `get_tendency_key`, and stores the result in `self.tendency`. If no values have been fetched yet, it calls `fetch_values` to do so.
        """

        self._tendency = self.tendency
        self.print_tendency()

    def print_tendency(self, print_first_value: bool = True, sfx: str = "\n") -> None:
        """
        Print the tendency of the comparison.

        Args:
            print_first_value (bool): Whether to print the first value. Defaults to True.
            sfx (str)               : The suffix to add after printing the second value and icon. Defaults to linebreak.
        """

        if print_first_value:
            self._kpis[0].print_function(f"  {self._kpis[0].value}%", end="")

        print(" => ", end="")
        self._kpis[1].print_function(f"{self._kpis[1].value}%", end="")
        self.tendency.print_function(self.tendency.icon, end=sfx)

    @override
    def __str__(self) -> str:
        """
        Convert the current instance into a string.

        Returns:
            str: a string representation of the current KPIComparator
        """

        return f"{self._kpis[0].value}% => {self._kpis[1].value}% {self.tendency.icon}"

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the current instance into a dictionary.

        Returns:
            dict[str, Any]: dictionary representation of the current instance
        """

        return {
            "kpi_perimeter": self.kpis[0].perimeter,
            "kpi_a_value": self.kpis[0].value,
            "kpi_b_value": self.kpis[1].value,
            "tendency": self.tendency.icon
        }

    # ****************************************************************
    # Static methods

    @staticmethod
    def compare_2_kpis(kpi_a: "KPI", kpi_b: "KPI") -> "KPIComparator":
        """
        Create a new instance of KPIComparator using the two provided KPI instances. It then runs the compare method of the comparator and returns it.

        Args:
            kpi_a (KPI): first KPI for the comparison
            kpi_b (KPI): second KPI for the comparison

        Returns:
            KPIComparator: the comparator instance once the compare action has been ran
        """

        comparator = KPIComparator(kpi_a, kpi_b)
        comparator.compare()

        return comparator

    @staticmethod
    def kpi_tuple_by_date(kpi_a: "KPI", kpi_b: "KPI") -> tuple["KPI", "KPI"]:
        """
        Return a tuple of 2 KPIs based on their dates.

        The first KPI of the tuple will be the one that was generated first (earlier).

        Args:
            kpi_a (KPI): first KPI
            kpi_b (KPI): second KPI

        Returns:
            tuple[KPI, KPI]: sorted tuple of KPI
        """

        return (kpi_a, kpi_b) if kpi_a.date < kpi_b.date else (kpi_b, kpi_a)
