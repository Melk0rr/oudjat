"""
A helper module to list ODBC drivers.
"""

from enum import Enum


class ODBCDriver(Enum):
    """
    A helper enum class to handle possible ODBC Drivers for SQL Servers.
    """

    SQL_SERVER = "{SQL Server}"
    SQL_SERVER_N = "{SQL Server Native Client}"
    SQL_SERVER_N10 = "{SQL Server Native Client 10.0}"
    SQL_SERVER_N11 = "{SQL Server Native Client 11.0}"
    ODBC_11 = "{ODBC Driver 11 for SQL Server}"
    ODBC_13  = "{ODBC Driver 13 for SQL Server}"
    ODBC_13_1  = "{ODBC Driver 13.1 for SQL Server}"
    ODBC_17 = "{ODBC Driver 17 for SQL Server}"
    ODBC_18 = "{ODBC Driver 18 for SQL Server}"
