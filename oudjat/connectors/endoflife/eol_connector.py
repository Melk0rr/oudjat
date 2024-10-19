from oudjat.connectors import Connector

EOL_API_URL = "https://endoflife.date/api/"

class EndOfLifeConnector(Connector):
  """ A class to connect to endoflife.date """
  
  # ****************************************************************
    # Attributes & Constructors

  def __init__(self):
    """ Construcotr """

    super().__init__(target=EOL_API_URL)

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