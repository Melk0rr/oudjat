from typing import List, Union

from oudjat.utils import ColorPrint
from oudjat.model.assets.computer import ComputerType
from . import OSFamily, Software, SoftwareType

class OperatingSystem(Software):
  """ A class to describe operating systems """
  
  # ****************************************************************
  # Attributes & Constructors
  
  def __init__(
    self,
    id: Union[int, str],
    name: str,
    label: str,
    os_family: OSFamily,
    computer_type: Union[Union[str, ComputerType], List[Union[str, ComputerType]]],
    editor: Union[str, List[str]] = None,
    description: str = None,
  ):
    """ Constructor """
    
    super().__init__(
      id=id,
      name=name,
      label=label,
      software_type=SoftwareType.OS,
      editor=editor,
      description=description
    )

    if not isinstance(computer_type, list):
      computer_type = [ computer_type ]
      
    self.computer_type = []
    for t in computer_type:
      if not isinstance(t, ComputerType):
        try:
          self.computer_type.append(ComputerType[t.upper()])

        except ValueError as e:
          ColorPrint.red(f"Could not add {t} as computer type")
      
      else:
        self.computer_type.append(t)
    

  # ****************************************************************
  # Methods
  