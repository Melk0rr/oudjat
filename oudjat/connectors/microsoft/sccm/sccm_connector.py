from ...connector import Connector


class SCCMConnector(Connector):
    
    # ****************************************************************
    # Attributes & Constructors

    def __init__(
        self, server: str, db_name: str, driver: str = "{SQL Server}", service_name: str = "OudjatSCCMConnection"
    ) -> None:
        """
        Create a new SCCMServer instance

        Args:
            server (str) :
            db_name (str):
            driver (str) :
        """

        super().__init__(target=server, service_name=service_name, use_credentials=True)
