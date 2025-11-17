"""A module to handle KPIs."""

from datetime import datetime
from enum import Enum
from typing import Any, Callable, NamedTuple, TypedDict, override

from oudjat.control.data import DataFilter, DataSet, DataSetType
from oudjat.control.data.data_filter import DataFilterDictionaryProps
from oudjat.utils import ColorPrint, DataType, TimeConverter
from oudjat.utils.types import DateInputType, NumberType


class ConformityLevelProps(NamedTuple):
    """
    A helper class to properly handle ConformityLevel types.

    Attributes:
        min: the minimum value for a level of conformity
        max: the maximum value for a level of conformity
        print_color: the print function used to print the KPI value
    """

    min: "NumberType"
    max: "NumberType"
    print_color: Callable[..., None]


class ConformityLevel(Enum):
    """Defines the levels of conformity for a KPI or any other related element."""

    NOTCONFORM = ConformityLevelProps(min=0, max=70, print_color=ColorPrint.red)
    PARTIALLYCONFORM = ConformityLevelProps(min=70, max=95, print_color=ColorPrint.yellow)
    CONFORM = ConformityLevelProps(min=95, max=100.01, print_color=ColorPrint.green)

    @property
    def min(self) -> "NumberType":
        """
        Return a ConformityLevel minimum value.

        Returns:
            float: minimum value of the conforimty level
        """

        return self._value_.min

    @property
    def max(self) -> "NumberType":
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


class KPIStaticProps(TypedDict):
    """
    A helper function to describe a KPI static attributes.

    Attributes:
        value (float)       : the value of the KPI
        date (DateInputType): the date the KPI was generated on
        scope_size (int)    : the input DataSet size
        conform_count (int) : the number of conform elements
    """

    value: float
    initial_set_size: int
    conform_count: int


class KPI(DataSet):
    """A class that aims to manipulate KPI and allow report of numbers and percentages regarding conformity of data sets."""

    # ****************************************************************
    # Attributes & Constructors

    def __init__(
        self,
        name: str,
        perimeter: str,
        date: "DateInputType | None" = None,
        static: "KPIStaticProps | None" = None,
        data_set: "DataSetType | None" = None,
        filters: list["DataFilterDictionaryProps"] | list["DataFilter"] | None = None,
        description: str | None = None,
    ) -> None:
        """
        Return a new instance of KPI.

        Args:
            name (str)                                                  : Name to assign to the new KPI
            perimeter (str)                                             : Perimeter of the new KPI
            date (datetime)                                             : The date the KPI is generated
            static (KPIStaticProps)                                     : KPI static values
            data_set (DataType | DataSet)                               : The scope the KPI is based on
            filters (list[DataFilterDictionaryProps] | list[DataFilter]): The filters the KPI result is based on
            description (str)                                           : A description of the KPI
        """

        super().__init__(
            name=name,
            perimeter=perimeter,
            initial_set=data_set,
            filters=filters,
            description=description,
        )

        self._static: "KPIStaticProps | None" = static

        if date is None:
            date = datetime.today()

        if isinstance(date, str):
            date = TimeConverter.str_to_date(date)

        self._date: datetime = date
        self._id: str = f"{perimeter.lower()}{TimeConverter.date_to_str(self._date)}"

        self._value: float | None = None

    # ****************************************************************
    # Methods

    @property
    def id(self) -> str:
        """
        Return the KPI id.

        Returns:
            str: generated ID of the current KPI
        """

        return self._id

    @property
    def date(self) -> datetime:
        """
        Return the generation date of the KPI.

        Returns:
            datetime: the date the KPI was generated
        """

        return self._date

    @date.setter
    def date(self, new_date: datetime) -> None:
        """
        Set the date that the KPI was generated.

        Args:
            new_date(datetime): datetime object describing the date of the KPI generation
        """

        self.date = new_date

    @property
    def conformity_level(self) -> "ConformityLevel":
        """
        Return the conformity level of the KPI based on its value.

        Args:
            value (float): the value of the KPI computed based on its scope and filters

        Returns:
            ConformityLevel: the computed level of conformity
        """

        def conformity_value_level(lvl: "ConformityLevel") -> bool:
            return lvl.min <= self.value <= lvl.max

        return next(filter(conformity_value_level, list(ConformityLevel)))

    @property
    def value(self) -> float:
        """
        Return the percentage of conform data based on kpi control.

        Returs:
            float: final KPI value which represent the percentage of conform data based on the KPI scope and filters
        """

        if self._static:
            return self._static["value"]

        if self._value is None:
            self._value = round(len(self.conform_elements) / len(self.initial_set_data) * 100, 2)

        return self._value

    @property
    def conform_elements(self) -> "DataType":
        """
        Return the output elements.

        More self-explanatory name for the super method "output_data" in the KPI context.

        Returns:
            DataType: list of conform elements that passed the instance filters.
        """

        return super().output_data

    @property
    def conform_count(self) -> int:
        """
        Return the number of conform elements.

        Returns:
            int: number of elements which passed the instance filters
        """

        return self._static["conform_count"] if self._static else len(self.conform_elements)

    @property
    def initial_set_size(self) -> int:
        """
        Return the number of initial elements.

        Returns:
            int: number of elements in the initial set data
        """

        return self._static["initial_set_size"] if self._static else len(self.initial_set_data)

    @property
    def print_function(self) -> Callable[..., None]:
        """
        Define and returns the print function to be used based on the KPI value and conformity level.

        Returns:
            Callable: print function to use with different color
        """

        return self.conformity_level.value.print_color

    @property
    def date_str(self) -> str:
        """
        Return formated date string.

        Returns:
            str: the generation date of the KPI formated as a string
        """

        return TimeConverter.date_to_str(self.date)

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

        set_str = str(self)

        print(prefix, end="")
        if print_details:
            print(f"{set_str[0]}", end=" = ")

        self.print_function(f"{set_str[1]}", end=f"{suffix}")

    @override
    def __str__(self) -> str:
        """
        Convert the current instance into a string.

        Returns:
            str: string representation of the current instance
        """

        return f"{self.conform_count} / {self.initial_set_size} => {self.value}"

    @override
    def to_dict(self) -> dict[str, Any]:
        """
        Convert the current instance into a dictionary.

        Returns:
            dict[str, Any]: A dictionary representation of the current kpi
        """

        base = super().to_dict()
        del base["output_data_size"]

        return {
            **base,
            "initial_set_size": self.initial_set_size,
            "conform_count": self.conform_count,
            "date": self.date_str,
            "value": self.value,
            "conformity": self.conformity_level.name,
        }

    # ****************************************************************
    # Static methods
