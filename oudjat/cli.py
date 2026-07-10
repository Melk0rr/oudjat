"""
Oudjat main entry point.
"""

import logging
import sys
from datetime import datetime
from typing import Any

from docopt import docopt

from oudjat.banner import banner
from oudjat.commands import (
    CERTFRConnectorCommand,
    CredentialUtilCmd,
    EOLConnectorCommand,
    LDAPConnectorCommand,
    S1ConnectorCommand,
    SCCMConnectorCommand,
    TenableSCConnectorCommand,
    VulnConnectorCommand,
)
from oudjat.commands.exceptions import UnknownCommand
from oudjat.utils import ColorPrint, Context, StdOutHook, TimeConverter
from oudjat.utils.doc_builder import DocBuilder
from oudjat.utils.logging import setup_logger

from . import __version__ as VERSION

_COMMAND_OPTIONS = {
    "connectors.edr.sentinelone": S1ConnectorCommand,
    "connectors.endoflife": EOLConnectorCommand,
    "connectors.cert.certfr": CERTFRConnectorCommand,
    "connectors.ldap": LDAPConnectorCommand,
    "connectors.sccm": SCCMConnectorCommand,
    "connectors.tenable.sc": TenableSCConnectorCommand,
    "connectors.vulns": VulnConnectorCommand,
    "utils.credentials": CredentialUtilCmd,
}


def _command_switch(options: dict[str, str]) -> Any:
    """
    Script command switch case.

    Args:
        options (dict[str, str]): CLI options
    """

    command_name = next(command for command in _COMMAND_OPTIONS.keys() if options.get(command))
    return _COMMAND_OPTIONS[command_name](options)


def _base_doc() -> "DocBuilder":
    """
    Return the base doc builder.

    Returns:
        DocBuilder: A doc builder instance containing the base program options and usages
    """

    description = """
Oudjat is a SOC toolbox that provides an entry point to various data sources.
It also allows for complex data consolidation and mapping through a config file system.

** The following doc string is dynamically generated based on the command you chose **"""

    builder = DocBuilder("oudjat", description)

    # builder.commands = {
    #     cmd.__cmd_props__.name: DocCommand(cmd.__cmd_props__.name, cmd.__cmd_props__.description)
    #     for cmd in _COMMAND_OPTIONS.values()
    # }

    builder.add_usage("--help", "-h | --help", "Prints a help message, then exit")
    builder.add_usage("--version", "-V | --version", "Prints the program version, then exit")

    for cmd_name, cmd in _COMMAND_OPTIONS.items():
        builder.add_command(cmd_name, cmd.__cmd_props__.description)

    builder.add_option("append", "Append to the output file", short="a")
    builder.add_option("help", "Print the doc string", short="h")
    builder.add_option("v", "Set log level to verbose", short="v")
    builder.add_option("vv", "Set log level to debug")
    builder.add_option("vvv", "Set log level to trace")
    builder.add_option(
        "output", "Specify a file to save the execution logs to", arg="LOGFILE", short="o"
    )
    builder.add_option("silent", "Simple output", short="S")
    builder.add_option("version", "Show the program version and exit", short="V")
    builder.add_option("csv", "Save results as a CSV file", arg="CSV")
    builder.add_option("json", "Save results as a JSON file", arg="JSON")
    builder.add_option("print", "Print the results in the terminal")
    builder.add_option("key-filter", "Filter the final result keys", arg="KEYFILTER")
    builder.add_option(
        "sort", "Sort the final result based on the provided key", short="s", arg="SORTKEY"
    )
    builder.add_option("sort-reverse", "Reverse the sorting order")

    builder.help_content = [
        "For help using this tool, please open an issue on the Codeberg repository:",
        "https://codeberg.org/me1k0r/oudjat",
    ]

    return builder


def _build_doc(cmd_name: str) -> "DocBuilder":
    """
    Return the final doc builder to be converted as a string and passed to docopt.

    Returns:
        DocBuilder: Final doc builder based on base doc and merged with the chosen command builder
    """

    doc = _base_doc()
    if _COMMAND_OPTIONS.get(cmd_name):
        cmd_builder = _COMMAND_OPTIONS[cmd_name].__doc_builder__
        doc.merge(cmd_builder)

    return doc


def main() -> None:
    """
    Program entry point that runs each time the 'oudjat' command line is executed.
    """

    context = Context()

    try:
        start_time = datetime.now().timestamp()

        if sys.argv[1] not in _COMMAND_OPTIONS and sys.argv[1] not in (
            "-h",
            "--help",
            "-V",
            "--version",
        ):
            raise UnknownCommand(f"{context}::Invalid command provided '{sys.argv[1]}'")

        __doc__ = _build_doc(sys.argv[1])
        options = docopt(str(__doc__), version=VERSION)

        original_stdout = sys.stdout

        if options["--output"] or options["--silent"]:
            sys.stdout = StdOutHook(
                options["--output"], options["--silent"], output=options["--output"]
            )

        logger = setup_logger(logging.INFO)

        if options["--v"]:
            logger.setLevel(logging.VERBOSE)

        elif options["--vv"]:
            logger.setLevel(logging.DEBUG)

        elif options["--vvv"]:
            logger.setLevel(logging.TRACE)

        ColorPrint.blue(banner)

        logger.info(
            f"{context}::Oudjat starts -  {datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S')} "
        )

        command = _command_switch(options)
        command.run()

        logger.info(
            f"Oudjat runtime -  {TimeConverter.seconds_to_str(datetime.now().timestamp() - start_time)}s"
        )

        if options["--output"]:
            assert isinstance(sys.stdout, StdOutHook)
            sys.stdout.write_out()

        sys.stdout = original_stdout

    except KeyboardInterrupt:
        print("\nQuitting...")
        sys.exit(0)
