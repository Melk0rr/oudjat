from typing import Dict, Tuple, Union

from oudjat.utils import ColorPrint

from . import KPI


class KPIComparator:
    """KPIComparator class to compare two KPIs"""

    tendencies = {
        "+": {"icon": "", "print": ColorPrint.green},
        "-": {"icon": "", "print": ColorPrint.red},
        "=": {"icon": "", "print": ColorPrint.yellow},
    }

    # ****************************************************************
    # Attributes & Constructors

    def __init__(self, kpi_a: KPI, kpi_b: KPI):
        """Constructor"""
        if kpi_a.get_perimeter() != kpi_b.get_perimeter():
            raise ValueError(f"{__class__} error : provided KPI do not share the same perimeter !")

        self.kpis = (kpi_a, kpi_b)

        self.values: Tuple[float, float] = ()
        self.tendency: Dict = None

    # ****************************************************************
    # Methods

    def get_kpis(self) -> Tuple[float, float]:
        """Getter for kpis"""
        return self.kpis

    def get_tendency(self) -> Dict:
        """Getter for comparator tendency"""
        return self.tendency

    def fetch_values(self) -> None:
        """Get kpis different values and set changes"""
        self.values = (self.kpis[0].get_kpi_value(), self.kpis[1].get_kpi_value())

    def get_tendency_key(self, v_a: Union[int, float], v_b: Union[int, float]) -> str:
        """Substract given values and define tendency"""
        return "+" if v_b > v_a else "-" if v_b < v_a else "="

    def compare(self) -> None:
        """Compare values and set tendency"""
        if len(self.values) == 0:
            self.fetch_values()

        t_key = self.get_tendency_key(self.values[0], self.values[1])
        self.tendency = self.tendencies[t_key]

    def print_tendency(self, print_first_value: bool = True, sfx: str = "\n") -> None:
        """Print tendency"""
        if print_first_value:
            self.kpis[0].get_print_function()(f"  {self.values[0]}%", end="")

        print(" -- ", end="")
        t_icon = self.tendency["icon"]
        self.kpis[1].get_print_function()(f"{self.values[1]}%", end="")
        self.tendency["print"](t_icon, end=sfx)

