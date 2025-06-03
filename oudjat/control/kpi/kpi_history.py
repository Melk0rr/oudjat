"""A module to track KPI history."""

from datetime import datetime
from typing import List

from oudjat.utils import ColorPrint

from .kpi import KPI
from .kpi_comparator import KPIComparator


class KPIHistory:
    """KPIEvolution class to handle."""

    def __init__(self, name: str, kpis: List[KPI] = []) -> None:
        """
        Create a new instance of KPIHistory.

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
        Add a KPI object to the list of KPIs if their names match.

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
        """Build the history of KPIs by comparing each pair in order based on their dates."""

        def kpi_date(kpi: "KPI") -> datetime:
            return kpi.get_date()

        sorted_kpis = sorted(self.kpis, kpi_date)

        self.comparators = [
            KPIComparator.compare_2_kpis(sorted_kpis[i], sorted_kpis[i + 1])
            for i in range(len(self.kpis) - 1)
        ]

    def print_history(self) -> None:
        """Print the history of KPIs by calling each comparator's print method to display their comparison results."""

        comparator_len = len(self.comparators)
        if comparator_len == 0:
            self.build_history()

        ColorPrint.blue(f"\n {self.name} History")

        for i in range(comparator_len):
            self.comparators[i].print_tendency(
                print_first_value=(i == 0), sfx=(i == comparator_len - 1) and "\n" or ""
            )
