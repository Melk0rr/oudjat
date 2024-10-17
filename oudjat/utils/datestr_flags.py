from enum import Enum

class DateStrFlag(Enum):
  """ Bit flag to handle date string format """
  YEAR  = 1 << 0
  MONTH = 1 << 1
  DAY   = 1 << 2
  HOUR  = 1 << 3
  MIN   = 1 << 4
  SEC   = 1 << 5
  

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
  
  if flags & DateStrFlag.YEAR:
    date_list.append("%Y")
    
  if flags & DateStrFlag.MONTH:
    date_list.append("%m")
  
  if flags & DateStrFlag.DAY:
    date_list.append("%d")
    
  if flags & DateStrFlag.HOUR:
    time_list.append("%H")
    
  if flags & DateStrFlag.MIN:
    time_list.append("%M")
    
  if flags & DateStrFlag.SEC:
    time_list.append("%S")
    
  date_str = date_sep.join(date_list)
  time_str = time_sep.join(time_list)
  
  return main_sep.join([ date_str, time_str ])