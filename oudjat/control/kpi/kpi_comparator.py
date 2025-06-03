"""A module to handle KPI comparisons."""

from typing import Dict, Tuple, Union

from oudjat.utils import ColorPrint

from .kpi import KPI


class KPIComparator:
    """A class to compare the results of 2 KPIs."""

    tendencies = {
        "+": {"icon": "", "print": ColorPrint.green},
        "-": {"icon": "", "print": ColorPrint.red},
        "=": {"icon": "", "print": ColorPrint.yellow},
    }

    # ****************************************************************
    # Attributes & Constructors

    def __init__(self, kpi_a: KPI, kpi_b: KPI) -> None:
        """
        Return a new instance of KPIComparator.

        Args:
            kpi_a (KPI): The first KPI object to compare.
            kpi_b (KPI): The second KPI object to compare.

        Raises:
            ValueError: If the provided KPIs do not share the same perimeter.
        """

        if kpi_a.get_perimeter() != kpi_b.get_perimeter():
            raise ValueError(
                f"{__class__.__name__}::Provided KPIs do not share the same perimeter !"
            )

        self.kpis = (kpi_a, kpi_b)

        self.values: Tuple[float, float] = ()
        self.tendency: Dict = None

    # ****************************************************************
    # Methods

    def get_kpis(self) -> Tuple[float, float]:
        """
        Getter for the KPIs being compared.

        Returns:
            Tuple[float, float]: A tuple containing the values of the two KPIs.
        """

        return self.kpis

    def get_tendency(self) -> Dict:
        """
        Getter for the comparator tendency.

        Returns:
            Dict: The current tendency represented as a dictionary with keys "icon" and "print".
        """

        return self.tendency

    def fetch_values(self) -> None:
        """
        Get the KPIs' different values and set the changes.

        This method retrieves the latest values of the provided KPIs and stores them in `self.values`.
        """

        self.values = (self.kpis[0].get_kpi_value(), self.kpis[1].get_kpi_value())

    def get_tendency_key(self, v_a: Union[int, float], v_b: Union[int, float]) -> str:
        """
        Subtract the given values and determine the tendency.

        Args:
            v_a (Union[int, float]): The first value to compare.
            v_b (Union[int, float]): The second value to compare.

        Returns:
            str: A string representing the tendency ("+" if v_b is greater than v_a, "-" if less, and "=" if equal).
        """

        return "+" if v_b > v_a else "-" if v_b < v_a else "="

    def compare(self) -> None:
        """
        Compare the values of the KPIs and set the tendency.

        This method compares the stored values of the KPIs, determines the tendency using `get_tendency_key`, and stores the result in `self.tendency`. If no values have been fetched yet, it calls `fetch_values` to do so.
        """

        if len(self.values) == 0:
            self.fetch_values()

        t_key = self.get_tendency_key(self.values[0], self.values[1])
        self.tendency = self.tendencies[t_key]

    def print_tendency(self, print_first_value: bool = True, sfx: str = "\n") -> None:
        """
        Print the tendency of the comparison.

        Args:
            print_first_value (bool): Whether to print the first value. Defaults to True.
            sfx (str): The suffix to add after printing the second value and icon. Defaults to linebreak.
        """

        if print_first_value:
            self.kpis[0].get_print_function()(f"  {self.values[0]}%", end="")

        print(" -- ", end="")
        self.kpis[1].get_print_function()(f"{self.values[1]}%", end="")
        self.tendency["print"](self.tendency["icon"], end=sfx)

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
