import re
from enum import Enum
from typing import Dict, List, Union

from oudjat.assets.computer.computer_type import ComputerType
from oudjat.utils.color_print import ColorPrint

from ..software import Software, SoftwareType
from ..software_release import SoftwareRelease


class OSFamily(Enum):
    """
    OS family enumeration

    """

    ANDROID = {
        "name": "android",
        "pattern": r"[Aa]ndroid|[Aa][Oo][Ss][Pp]|[Gg]raphene[Oo][Ss]|[Ll]ineage[Oo][Ss]|\/e\/[Oo][Ss]|[Cc]alyx[Oo][Ss]",
    }

    BSD = {"name": "bsd", "pattern": r"[Bb][Ss][Dd]"}

    LINUX = {
        "name": "linux",
        "pattern": r"[Dd]ebian|[Uu]buntu|[Mm]int|[Nn]ix[Oo][Ss]|(?:[Oo]pen)?[Ss][Uu][Ss][Ee]|[Ff]edora|[Rr](?:ed )?[Hh](?:at )?[Ee](?:nterprise )?[Ll](?:inux)?|[Oo]racle(?: Linux)?",
    }

    MAC = {"name": "mac", "pattern": r"[Mm][Aa][Cc](?:[Oo][Ss])?"}

    WINDOWS = {"name": "windows", "pattern": r"[Ww]indows(?: [Ss]erver)?"}

    @property
    def name(self) -> str:
        """
        Get the name of the operating system family.

        Returns:
            str: The name of the OS family as a string.
        """

        return self._value_["name"]

    @property
    def pattern(self) -> str:
        """
        Get the regex pattern for the operating system family.

        Returns:
            str: The regex pattern as a string.
        """

        return self._value_["pattern"]


class OperatingSystem(Software):
    """A class to describe operating systems"""

    # ****************************************************************
    # Attributes & Constructors

    def __init__(
        self,
        os_id: Union[int, str],
        name: str,
        label: str,
        os_family: OSFamily,
        computer_type: Union[Union[str, ComputerType], List[Union[str, ComputerType]]],
        editor: Union[str, List[str]] = None,
        description: str = None,
    ) -> None:
        """
        Returns a new instance of OperatingSystem

        Args:
            os_id (int | str)                       : OS unique ID
            name (str)                              : the name of the operating system
            label (str)                             : a short string to labelize the os
            os_family (OSFamily)                    : family of operating system, usually (Linux, MAC, Windows)
            computer_type (List[str | ComputerType]): the type(s) of computer the OS is tide to
            editor (str | List[str])                : the editor in charge of the OS maintenance and/or development
            description (str)                       : a string to describe the OS
        """

        super().__init__(
            software_id=id,
            name=name,
            label=label,
            software_type=SoftwareType.OS,
            editor=editor,
            description=description,
        )

        if not isinstance(computer_type, list):
            computer_type = [computer_type]

        self.computer_type = []
        for t in computer_type:
            if not isinstance(t, ComputerType):
                try:
                    self.computer_type.append(ComputerType[t.upper()])

                except ValueError:
                    ColorPrint.red(f"Could not add {t} as computer type")

            else:
                self.computer_type.append(t)

        self.os_family = os_family

    # ****************************************************************
    # Methods

    def get_computer_type(self) -> List[ComputerType]:
        """
        Returns the computer types related to the current OS

        Returns:
            List[ComputerType]: the list of computer types as ComputerType enumeration elements
        """

        return self.computer_type

    def get_os_family(self) -> OSFamily:
        """
        Returns the OS family of the current OS

        Returns:
            OSFamily: the OS family represented by an OSFamily enumeration element
        """

        return self.os_family

    def gen_releases(self) -> None:
        """
        This method must generate the list of releases of the current OS
        It must be overwritten by the classes inheriting OperatingSystem
        """

        raise NotImplementedError(
            f"{__class__.__name__}.gen_releases::Method must be implemented by the overloading class"
        )

    # ****************************************************************
    # Static methods

    @staticmethod
    def get_matching_os_family(test_str: str) -> str:
        """
        Tries to retrieve a substring of the provided string matching an OSFamily element

        Args:
            test_str (str): provided string that possibly matches an OSFamily element

        Returns:
            str: substring that match an OSFamily element
        """

        if test_str is None:
            return None

        for f in OSFamily:
            search = re.search(f.pattern, test_str)
            if search is not None:
                return search.group(0)

    @staticmethod
    def get_matching_version(test_str: str) -> str:
        """
        This static method uses a regular expression to find and return a version number from the input string.
        It must be implemented by the class inheriting OperatingSystem

        Args:
            test_str (str): The string to search for a version match.

        Returns:
            str: A string representing the matched version, or None if no match is found.
        """

        raise NotImplementedError(
            f"{__class__.__name__}.get_matching_version::Method must be implemented by the overloading class"
        )


class OSRelease(SoftwareRelease):
    """Specific software release for OperatingSystem"""

    # ****************************************************************
    # Methods

    def get_name(self) -> str:
        """
        Returns the OS release name
        Must be implemented by overloading classes

        Returns:
            str: forged name of the OS release
        """

        raise NotImplementedError(
            f"{__class__.__name__}.get_name()::Method must be implemented by the overloading class"
        )

    def get_os(self) -> OperatingSystem:
        """
        Returns the operating system instance tide to the current release

        Returns:
            OperatingSystem: operating system instance of the current release
        """

        return self.software

    def to_dict(self) -> Dict:
        """
        Converts the current instance into a dictionary

        Returns:
            Dict: dictionary representation of the current instance
        """

        base_dict = super().to_dict()
        os_name = base_dict.pop("software")

        return {"os": os_name, **base_dict}
