import os

from typing import List, Dict, Any, Union

from oudjat.connectors.connector import Connector
from oudjat.control.data.data_filter import DataFilter
from oudjat.connectors.file.file_types import FileTypes

def check_path(path: str) -> None:
  """ Check if the provided path is valid """
  if not os.path.isfile(path):
    raise(f"Invalid file path provided: {path}")
    
  file_ext = path.split('.')[-1]
  if file_ext.upper() not in FileTypes.__members__:
    raise ValueError(f"Invalid filetype provided: {file_ext}")

class FileConnector(Connector):
  """ File connector to interact with different file types """
  
  def __init__(self, path: str, source: str):
    """ Constructor """
    check_path(path)
    file_ext = path.split('.')[-1]
    
    self.source = source
    self.filetype = FileTypes[file_ext.upper()]
    self.import_function = self.filetype.value.get("import")

    self.connection = False
    self.data = None
    super().__init__(path, service_name=None, use_credentials=False)

  def get_data(self) -> List[Any]:
    """ Getter for file data """
    if not self.connection:
      self.connect()
    
    return self.data
    
  def set_path(self, new_path: str) -> None:
    """ Setter for connector path """
    check_path(new_path)
    self.target = new_path
    
  def connect(self) -> None:
    """ 'Connects' to the file and uses the """
    raise NotImplementedError(
      "data() method must be implemented by the overloading class")

  def disconnect(self) -> None:
    """ 'Disconnects' from the targeted file """
    self.data = None
    self.connection = False
    
  def search(
    self,
    search_filter: List[Dict],
    attributes: Union[str, List[str]] = None
  ) -> List[Any]:
    """ Searches into the imported data """
    
    if not self.connection:
      self.connect()
      
    res = []
    
    for el in self.data:
      conditions = DataFilter.get_conditions(el, filters=search_filter)
      
      if conditions:
        res.append({ k: v } for k,v in el if k in attributes)
        
    return res
    
    
class CSVConnector(FileConnector):
  """ Specific file connector for CSV files """
  
  def __init__(self, path: str, source: str, delimiter: str = '|'):
    """ Constructor """
    if len(delimiter) > 1:
      raise("Invalid delimiter provided. Please provide a single character")
    
    self.delimiter = delimiter
    super().__init__(path, source)
    
  def connect(self, callback: object) -> List[Any]:
    """ Implementation of parent function """
    try:
      self.data = self.import_function(file_path=self.target, delimiter=self.delimiter, callback=callback)
      self.connection = True

    except Exception as e:
      raise(f"CSVConnector::Error connecting to file {self.target}\n{e}")
    