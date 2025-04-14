# INFO: KPI module handling operations related to indicators

from datetime import datetime
from enum import Enum
from typing import Callable, Dict, List, Union

from oudjat.control.data import DataFilter, DataSet
from oudjat.utils import ColorPrint


class ConformityLevel(Enum):
    """Defines the levels of conformity for a KPI or any other related element"""

    NOTCONFORM = {"min": 0, "max": 70, "color": ColorPrint.red}
    PARTIALLYCONFORM = {"min": 70, "max": 95, "color": ColorPrint.yellow}
    CONFORM = {"min": 95, "max": 100.01, "color": ColorPrint.green}


class KPI(DataSet):
    """KPI class"""

    # ****************************************************************
    # Attributes & Constructors

    def __init__(
        self,
        name: str,
        perimeter: str,
        scope: Union[List[Dict], DataSet] = None,
        filters: Union[List[Dict], List[DataFilter]] = [],
        description: str = None,
        date: datetime = None,
    ) -> None:
        """
        Returns a new instance of KPI

        Args:
            name (str)                             : name to assign to the new KPI
            perimeter (str)                        : perimeter of the new KPI
            scope (List[Dict] | DataSet)           : the scope the KPI is based on
            filters (List[Dict] | List[DataFilter]): the filters the KPI result is based on
            description (str)                      : a description of the KPI
            date (datetime)                        : the date the KPI is generated
        """

        super().__init__(
            name=name, perimeter=perimeter, scope=scope, filters=filters, description=description
        )

        if date is None:
            date = datetime.today()

        self.date: datetime = date

    # ****************************************************************
    # Methods

    def get_date(self) -> datetime:
        """
        Returns the generation date of the KPI

        Returns:
            datetime: the date the KPI was generated
        """

        return self.date

    def get_conformity_level(self, value: float = None) -> "ConformityLevel":
        """
        Returns the conformity level of the KPI based on its value

        Args:
            value (float): the value of the KPI computed based on its scope and filters

        Returns:
            ConformityLevel: the computed level of conformity
        """

        if value is None:
            value = self.get_kpi_value()

        conformity_lvls = list(ConformityLevel)
        return next(
            filter(KPI.conformity_value_level, conformity_lvls, [value] * len(conformity_lvls))
        )

    def get_kpi_value(self) -> float:
        """
        Returns the percentage of conform data based on kpi control

        Returs:
            float: final KPI value which represent the percentage of conform data based on the KPI scope and filters
        """

        return round(len(self.get_data()) / len(self.get_input_data()) * 100, 2)

    def get_print_function(self) -> Callable:
        """
        Defines and returns the print function to be used based on the KPI value and conformity level

        Returns:
            Callable: print function to use with different color
        """

        return self.get_conformity_level().value["color"]

    def print_value(
        self, prefix: str = None, suffix: str = "%\n", print_details: bool = True
    ) -> None:
        """
        Prints value with color based on kpi level

        Args:
            prefix (str)        : string to include as prefix to the printed infos
            suffix (str)        : string to include as suffix to the printed infos
            print_details (bool): include additional details to the printed infos
        """
        scope_str = str(self)

        print(prefix, end="")
        if print_details:
            print(f"{scope_str[0]}", end=" = ")

        self.get_print_function()(f"{scope_str[1]}", end=f"{suffix}")

    def get_date_str(self) -> str:
        """
        Returns formated date string

        Returns:
            str: the generation date of the KPI formated as a string
        """

        return self.date.strftime("%Y-%m-%d")

    def __str__(self) -> str:
        """
        Converts the current instance into a string

        Returns:
            str: string representation of the current instance
        """

        return f"{len(self.get_data())} / {len(self.get_input_data())} = {self.get_kpi_value()}"

    def to_dict(self) -> Dict:
        """
        Converts the current instance into a dictionary

        Returns:
            Dict : dictionary representation of the current kpi
        """

        k_value = self.get_kpi_value()
        conformity = self.get_conformity_level(k_value)

        return {
            "name": self.name,
            "perimeter": self.perimeter,
            "scope": self.get_initial_scope_name(),
            "scope_size": len(self.get_input_data()),
            "conform_elements": len(self.get_data()),
            "value": k_value,
            "conformity": conformity.name,
            "date": self.get_date_str(),
        }

    # ****************************************************************
    # Static methods

    def conformity_value_level(lvl: ConformityLevel, value: float) -> bool:
        """
        Checks if the given value is between the provided conformity level min and max values

        Args:
            lvl (ConformityLevel): conformity level to compare with provided value
            value (flaot)        : value that will be compared to the provided conformity level

        Returns:
            bool: True if the provided value matches the given conforimty level, False otherwise
        """
        return lvl.value["min"] <= value <= lvl.value["max"]
