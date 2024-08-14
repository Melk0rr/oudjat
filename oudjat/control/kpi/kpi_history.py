from typing import List

from oudjat.utils.color_print import ColorPrint
from oudjat.control.kpi.kpi import KPI
from oudjat.control.kpi.kpi_comparator import KPIComparator

class KPIHistory:
  """ KPIEvolution class to handle """

  def __init__(self, name: str, kpis: List[KPI] = []):
    """ Constructor """
    self.name = name
    self.kpis = []

    self.comparators = []

  def get_kpis(self):
    """ Getter for kpi list """
    return self.kpis

  def set_kpis(self, kpis: List[KPI] = []) -> None:
    """ Setter for kpi list """
    for k in kpis:
      self.add_kpi(k)

  def add_kpi(self, kpi: "KPI") -> None:
    """ Add a kpi to the kpi list """
    if self.name != kpi.get_name():
      raise ValueError(f"{__class__} error while adding new kpi. KPI name and KPIHistory name must match !")

    self.kpis.append(kpi)

  def build_history(self) -> None:
    """ Builds the KPI history """
    comp_list = []
    sorted_kpis = sorted(self.kpis, key=lambda k: k.get_date())

    for i in range(len(self.kpis) - 1):
      comparator = KPIComparator(sorted_kpis[i], sorted_kpis[i + 1])
      comparator.compare()

      comp_list.append(comparator)
    
    self.comparators = comp_list

  def print_history(self) -> None:
    """ Print the KPI history """
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