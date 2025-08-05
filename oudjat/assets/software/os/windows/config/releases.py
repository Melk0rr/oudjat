"""A module that defines Windows releases."""

from typing import Any, NamedTuple

from oudjat.utils.file_utils import FileHandler


class MSRealeaseProps(NamedTuple):
    """A class to properly handle MS release types."""

    os: str
    release_label: str
    release_date: str
    support: str
    eol: str
    lts: bool
    latest: str
    link: str
    edition: list[str]

    @staticmethod
    def from_dictionary(rel_dictionary: dict[str, Any]) -> "MSRealeaseProps":
        """
        Create a new MSRealeaseProps from a dictionary.

        Args:
            rel_dictionary (dict[str, Any]): dictionary containing ms release informations

        Returns:
            MSRealeaseProps: new MSRealeaseProps
        """

        return MSRealeaseProps(
            os=rel_dictionary["os"],
            release_label=rel_dictionary["releaseLabel"],
            release_date=rel_dictionary["releaseDate"],
            support=rel_dictionary["support"],
            eol=rel_dictionary["eol"],
            lts=rel_dictionary["lts"],
            latest=rel_dictionary["latest"],
            link=rel_dictionary.get("link", ""),
            edition=rel_dictionary.get("edition", []),
        )


release_import: list[dict[str, Any]] = FileHandler.import_json("./releases.jsonc")[0]

if not isinstance(release_import, dict):
    raise ValueError("Releases import must be a dictionary")

WINDOWS_RELEASES: dict[str, list[MSRealeaseProps]] = {
    os_label: list(map(MSRealeaseProps.from_dictionary, os_releases))
    for os_label, os_releases in release_import.items()
}
