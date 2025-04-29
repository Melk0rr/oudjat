from typing import List

from oudjat.utils import ColorPrint

from .kpi import KPI
from .kpi_comparator import KPIComparator


class KPIHistory:
    """KPIEvolution class to handle"""

    def __init__(self, name: str, kpis: List[KPI] = []):
        """
        Constructor for the KPIHistory class.

        Args:
            name (str)                : The name of the object instance.
            kpis (List[KPI], optional): A list of KPI objects to initialize with. Defaults to an empty list.
        """

        self.name = name
        self.kpis = []

        self.comparators = []

    def get_kpis(self):
        """
        Getter for the kpi list.

        Returns:
            List[KPI]: The list of KPI objects associated with this instance.
        """

        return self.kpis

    def set_kpis(self, kpis: List[KPI] = []) -> None:
        """
        Setter for the kpi list. Updates the list of KPIs in the class.

        Args:
            kpis (List[KPI], optional): A list of KPI objects to set. Defaults to an empty list.
        """

        for k in kpis:
            self.add_kpi(k)

    def add_kpi(self, kpi: "KPI") -> None:
        """
        Adds a KPI object to the list of KPIs if their names match.

        Args:
            kpi (KPI): The KPI object to be added.

        Raises:
            ValueError: If the name of the provided KPI does not match the instance's name.
        """

        if self.name != kpi.get_name():
            raise ValueError(
                f"{__class__.__name__}.add_kpi::KPI name and KPIHistory name must match !"
            )

        self.kpis.append(kpi)

    def build_history(self) -> None:
        """
        Builds the history of KPIs by comparing each pair in order based on their dates.
        """

        comp_list = []
        sorted_kpis = sorted(self.kpis, key=lambda k: k.get_date())

        for i in range(len(self.kpis) - 1):
            comparator = KPIComparator(sorted_kpis[i], sorted_kpis[i + 1])
            comparator.compare()

            comp_list.append(comparator)

        self.comparators = comp_list

    def print_history(self) -> None:
        """
        Prints the history of KPIs by calling each comparator's print method to display their comparison results.
        """

        if len(self.comparators) == 0:
            self.build_history()

        ColorPrint.blue(f"\n {self.name} History")
        for i in range(len(self.comparators)):
            c = self.comparators[i]

            print_first = False
            print_end = ""

            if i == 0:
                print_first = True

            if i == len(self.comparators) - 1:
                print_end = "\n"

            c.print_tendency(print_first_value=print_first, sfx=print_end)
