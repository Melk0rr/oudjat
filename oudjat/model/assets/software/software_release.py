from datetime import datetime
from typing import List, Dict, Union, TYPE_CHECKING

from oudjat.utils import date_format_from_flag, DATE_FLAGS, days_diff

from .software_support import SoftwareReleaseSupport, SoftwareReleaseSupportList, soft_date_str

if TYPE_CHECKING:
    from .software import Software


class SoftwareRelease:
    """A class to describe software releases"""

    # ****************************************************************
    # Attributes & Constructors

    def __init__(
        self,
        software: "Software",
        version: Union[int, str],
        release_date: Union[str, datetime],
        release_label: str,
    ):
        """Constructor"""

        self.software = software
        self.version = version
        self.label = release_label

        try:
            if not isinstance(release_date, datetime):
                release_date = datetime.strptime(release_date, date_format_from_flag(DATE_FLAGS))

        except ValueError as e:
            raise ValueError(f"Please provide dates with %Y-%m-%d format\n{e}")

        self.release_date = release_date
        self.support = SoftwareReleaseSupportList()
        self.vulnerabilities = set()

    # ****************************************************************
    # Methods

    def get_software(self) -> "Software":  # noqa: F821
        """Getter for release software"""
        return self.software

    def get_label(self) -> str:
        """Getter for release label"""
        return self.label

    def get_version(self) -> Union[int, str]:
        """Getter for release version"""
        return self.version

        return days_diff(self.end_of_life, reverse=True) > 0

    def is_supported(self, edition: Union[str, List[str]] = None) -> bool:
        """Checks if the current release has an ongoin support"""
        return any(
            [
                s.is_ongoing() and (edition is None or s.supports_edition(edition))
                for s in self.support
            ]
        )

    def get_support(self) -> SoftwareReleaseSupportList:
        """Getter for support list"""
        return self.support

    def get_support_for_edition(
        self, edition: Union[str, List[str]], lts: bool = False
    ) -> SoftwareReleaseSupportList:
        """Returns support for given edition"""
        if edition is None:
            return None

        return self.support.get(edition, lts=lts)

    def get_ongoing_support(self) -> List[SoftwareReleaseSupport]:
        """Returns ongoing support instances"""
        return [s for s in self.support if s.is_ongoing()]

    def get_retired_support(self) -> List[SoftwareReleaseSupport]:
        """Returns retired support instances"""
        return [s for s in self.support if not s.is_ongoing()]

    def get_name(self) -> None:
        """Method to generate releases"""
        raise NotImplementedError("get_name() method must be implemented by the overloading class")

    def get_full_name(self) -> None:
        """Method to generate releases"""
        return f"{self.get_software().get_name()} {self.label}"

    def add_support(self, support: SoftwareReleaseSupport) -> None:
        """Adds a support instance to the current release"""
        if not isinstance(support, SoftwareReleaseSupport):
            return

        if not self.support.contains(
            edition=support.get_edition(), lts=support.has_long_term_support()
        ):
            self.support.append(support)

    def has_vulnerability(self, vuln: Union[str, List[str]] = None) -> List[str]:
        """Check if the release is concerned by any or specific vulnerability"""
        if vuln is None:
            return list(self.vulnerabilities)

        if not isinstance(vuln, list):
            vuln = [vuln]

        return [v in self.vulnerabilities for v in vuln]

    def add_vuln(self, vuln: str) -> None:
        """Adds a vulnerability to the current release"""
        self.vulnerabilities.add(vuln)

    def __str__(self, show_version: bool = False) -> str:
        """Converts current release to a string"""
        name = self.get_full_name()

        if show_version:
            name = f"{name.strip()}({self.version})"

        return name.strip()

    def os_info_dict(self) -> Dict:
        """Returns a dictionary with os infos"""
        return {
            "software": self.get_software().get_name(),
            "name": self.get_name(),
            "version": self.version,
            "full_name": self.get_full_name(),
            "is_supported": self.is_supported(),
        }

    def to_dict(self) -> Dict:
        """Converts current release into a dict"""
        return {
            "label": self.label,
            "release_date": soft_date_str(self.release_date),
            **self.os_info_dict(),
            "support": ", ".join([str(s) for s in self.support]),
        }


class SoftwareReleaseDict(dict):
    """Software release dictionary"""

    def find_rel_matching_label(self, val: str) -> "SoftwareReleaseDict":
        """Try to find release with a label matching the given string"""
        return {k: v for k, v in self.items() if k in val}

    def find_rel(self, rel_ver: str, rel_label: str = None) -> "SoftwareReleaseDict":
        """Finds the given release"""
        ver_search = self.get(rel_ver, None)
        lab_search = None

        if ver_search is not None and rel_label is not None:
            lab_search = ver_search.get(rel_label, None)

        return ver_search if lab_search is None else {lab_search.get_label(): lab_search}

