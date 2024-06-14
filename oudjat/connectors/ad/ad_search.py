from oudjat.connectors.ad.ad_filters import ADSearchFilters
from oudjat.connectors.ad.ad_attributes import ADAttributes

class ADSearch:
  """ Helper class to define an Active Directory class """

  def __init__(
    self,
    connector: "ADConnector",
    search_base: str = None,
    search_filter: str = None,
    attributes: List[str] = []
  ):
    """ Constructor """
    self.connector = connector

    # Handling search base
    if search_base is None:
      search_base = self.connector.get_default_search_base()
      
    self.search_base = search_base
    
    # Handling search filter : default is user filter
    if search_filter is None:
      search_filter = ADSearchFilters.user.value

    self.search_filter = search_filter

    # Handling search attributes
    if len(attributes) == 0:
      attributes = ADAttributes.user.value
      
    self.attributes = attributes
  
  def clean_results(self, search_result: List[Dict]):
    """ Filter results to keep only searchResEntry and remove useless attributes """
    return [ { "dn": e.get("dn", ""), **e.get("attributes", {}) } for e in search_result if e["type"] == "searchResEntry" ]
    
  def run(self, auto_clean: bool = True):
    """ Runs the search based on current base, filter and attributes """
    search = self.connector.get_connection().extend.standard.paged_search(
      search_base=self.search_base,
      search_filter=self.search_filter,
      attributes=self.attributes,
      search_scope=SUBTREE,
      generator=False
    )
    
    if auto_clean:
      search = self.clean_results(search)
    
    return search
