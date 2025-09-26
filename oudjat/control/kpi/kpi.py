"""A module to handle KPIs."""

from datetime import datetime
from enum import Enum
from typing import Any, Callable, NamedTuple, override

from oudjat.control.data import DataFilter, DataSet
from oudjat.control.data.data_filter import DataFilterDictionaryProps
from oudjat.utils import ColorPrint, TimeConverter
from oudjat.utils.types import DateInputType, NumberType


class ConformityLevelProps(NamedTuple):
    """
    A helper class to properly handle ConformityLevel types.

    Attributes:
        min: the minimum value for a level of conformity
        max: the maximum value for a level of conformity
        print_color: the print function used to print the KPI value
    """

    min: NumberType
    max: NumberType
    print_color: Callable[..., None]


class ConformityLevel(Enum):
    """Defines the levels of conformity for a KPI or any other related element."""

    NOTCONFORM = ConformityLevelProps(min=0, max=70, print_color=ColorPrint.red)
    PARTIALLYCONFORM = ConformityLevelProps(min=70, max=95, print_color=ColorPrint.yellow)
    CONFORM = ConformityLevelProps(min=95, max=100.01, print_color=ColorPrint.green)

    @property
    def min(self) -> NumberType:
        """
        Return a ConformityLevel minimum value.

        Returns:
            float: minimum value of the conforimty level
        """

        return self._value_.min

    @property
    def max(self) -> NumberType:
        """
        Return a ConformityLevel maximum value.

        Returns:
            float: maximum value of the conforimty level
        """

        return self._value_.max

    @property
    def print_color(self) -> Callable[[str], None]:
        """
        Return a ConformityLevel color print function.

        Returns:
            Callable[[str], None]: conformity level function to print value in a certain color
        """

        return self._value_.print_color


class KPI(DataSet):
    """A class that aims to manipulate KPI and allow report of numbers and percentages regarding conformity of data sets."""

    # ****************************************************************
    # Attributes & Constructors

    def __init__(
        self,
        name: str,
        perimeter: str,
        date: DateInputType | None = None,
        data_set: list[dict[str, Any]] | DataSet | None = None,
        filters: list[DataFilterDictionaryProps] | list[DataFilter] | None = None,
        description: str | None = None,
    ) -> None:
        """
        Return a new instance of KPI.

        Args:
            name (str)                               : name to assign to the new KPI
            perimeter (str)                          : perimeter of the new KPI
            data_set (list[dict[str, Any]] | DataSet): the scope the KPI is based on
            filters (List[Dict] | List[DataFilter])  : the filters the KPI result is based on
            description (str)                        : a description of the KPI
            date (datetime)                          : the date the KPI is generated
        """

        super().__init__(
            name=name,
            perimeter=perimeter,
            initial_set=data_set,
            filters=filters,
            description=description,
        )

        if date is None:
            date = datetime.today()

        if isinstance(date, str):
            date = TimeConverter.str_to_date(date)

        self.date: datetime = date
        self._id: str = f"{perimeter.lower()}{TimeConverter.date_to_str(self.date)}"

    # ****************************************************************
    # Methods

    def get_id(self) -> str:
        """
        Return the KPI id.

        Returns:
            str: generated ID of the current KPI
        """

        return self._id

    def get_date(self) -> datetime:
        """
        Return the generation date of the KPI.

        Returns:
            datetime: the date the KPI was generated
        """

        return self.date

    def get_conformity_level(self, value: float | None = None) -> "ConformityLevel":
        """
        Return the conformity level of the KPI based on its value.

        Args:
            value (float): the value of the KPI computed based on its scope and filters

        Returns:
            ConformityLevel: the computed level of conformity
        """

        value = value or self.get_kpi_value()

        def conformity_value_level(lvl: "ConformityLevel") -> bool:
            return lvl.min <= value <= lvl.max

        return next(filter(conformity_value_level, list(ConformityLevel)))

    def get_kpi_value(self) -> float:
        """
        Return the percentage of conform data based on kpi control.

        Returs:
            float: final KPI value which represent the percentage of conform data based on the KPI scope and filters
        """

        return round(len(self.output_data) / len(self.input_data) * 100, 2)

    def get_print_function(self) -> Callable[..., None]:
        """
        Define and returns the print function to be used based on the KPI value and conformity level.

        Returns:
            Callable: print function to use with different color
        """

        return self.get_conformity_level().value.print_color

    def print_value(
        self, prefix: str | None = None, suffix: str = "%\n", print_details: bool = True
    ) -> None:
        """
        Print value with color based on kpi level.

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
        Return formated date string.

        Returns:
            str: the generation date of the KPI formated as a string
        """

        return TimeConverter.date_to_str(self.date)

    @override
    def __str__(self) -> str:
        """
        Convert the current instance into a string.

        Returns:
            str: string representation of the current instance
        """

        return f"{len(self.output_data)} / {len(self.input_data)} = {self.get_kpi_value()}"

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the current instance into a dictionary.

        Returns:
            Dict : dictionary representation of the current kpi
        """

        k_value = self.get_kpi_value()
        conformity = self.get_conformity_level(k_value)

        return {
            "name": self.name,
            "perimeter": self.perimeter,
            "scope": self.initial_set_name,
            "scope_size": len(self.input_data),
            "conform_elements": len(self.output_data),
            "value": k_value,
            "conformity": conformity.name,
            "date": self.get_date_str(),
        }

    # ****************************************************************
    # Static methods
