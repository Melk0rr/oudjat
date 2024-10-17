from enum import Flag, auto

class DateStrFlag(Enum):
  """ Bit flag to handle date string format """
  YEAR  = auto()
  MONTH = auto()
  DAY   = auto()
  HOUR  = auto()
  MIN   = auto()
  SEC   = auto()
  

DATE_FLAGS = DateStrFlag.YEAR | DateStrFlag.MONTH | DateStrFlag.DAY
TIME_FLAGS = DateStrFlag.HOUR | DateStrFlag.MIN | DateStrFlag.SEC
DATE_TIME_FLAGS = DATE_FLAGS | TIME_FLAGS

def date_format_from_flag(
  flags: DateStrFlag,
  date_sep: str = '-',
  time_sep: str = ':',
  main_sep: str = ' '
) -> str:
  """ Generate a datestring format based on a given flag """
  date_list = []
  time_list = []
  
  if DateStrFlag.YEAR in flags:
    date_list.append("%Y")
    
  if DateStrFlag.MONTH in flags:
    date_list.append("%m")
  
  if DateStrFlag.DAY in flags:
    date_list.append("%d")
    
  if DateStrFlag.HOUR in flags:
    time_list.append("%H")
    
  if DateStrFlag.MIN in flags:
    time_list.append("%M")
    
  if DateStrFlag.SEC in flags:
    time_list.append("%S")
    
  date_str = date_sep.join(date_list)
  time_str = time_sep.join(time_list)
  
  return main_sep.join([ date_str, time_str ])