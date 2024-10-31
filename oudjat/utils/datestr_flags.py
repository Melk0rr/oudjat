from enum import Enum

class DateStrFlag(Enum):
  """ Bit flag to handle date string format """
  YEAR  = 1 << 0
  MONTH = 1 << 1
  DAY   = 1 << 2
  HOUR  = 1 << 3
  MIN   = 1 << 4
  SEC   = 1 << 5
  
class DateFormatChar(Enum):
  """ Date format characters """
  YEAR  = "%Y"
  MONTH = "%m"
  DAY   = "%d"

class TimeFormatChar(Enum):
  """ Time format characters """
  HOUR  = "%H"
  MIN   = "%M"
  SEC   = "%S"

DATE_FLAGS = DateStrFlag.YEAR.value | DateStrFlag.MONTH.value | DateStrFlag.DAY.value
TIME_FLAGS = DateStrFlag.HOUR.value | DateStrFlag.MIN.value | DateStrFlag.SEC.value
DATE_TIME_FLAGS = DATE_FLAGS | TIME_FLAGS

def check_date_flag(format_val: int, date_flag: DateStrFlag) -> int:
  """ Compare value to given date string flag """
  return format_val & date_flag.value

def date_format_from_flag(
  date_flags: int,
  date_sep: str = '-',
  time_sep: str = ':',
  main_sep: str = ' '
) -> str:
  """ Generate a datestring format based on a given flag """

  date_str = date_sep.join([ c.value for c in DateFormatChar if check_date_flag(date_flags, DateStrFlag[c.name]) ])
  time_str = time_sep.join([ c.value for c in TimeFormatChar if check_date_flag(date_flags, DateStrFlag[c.name]) ])
  
  return main_sep.join([ date_str, time_str ]).strip()