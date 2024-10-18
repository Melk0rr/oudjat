from oudjat.connectors import Connector

class EndOfLifeConnector(Connector):
  """ A class to connect to endoflife.date """
  
  # ****************************************************************
    # Attributes & Constructors

  def __init__(self):
    """ Construcotr """

    super().__init__(target="https://endoflife.date/api/")
    self.connection = None

  # ****************************************************************
  # Methods

  def connect(self) -> None:
    """ Connects to target """
    
  def search(
    self,
    search_filter: Union[str, List[str]],
    attributes: Union[str, List[str]] = None
  ) -> List[Dict]:
    """ Searches the API for product infos """