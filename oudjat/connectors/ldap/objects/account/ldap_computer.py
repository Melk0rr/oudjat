"""A module to handle manipulation of LDAP computer objects."""

from typing import TYPE_CHECKING, Any

from oudjat.assets.computer import Computer
from oudjat.assets.software import SoftwareEdition, SoftwareRelease
from oudjat.assets.software.os import OperatingSystem, OSOption
from oudjat.assets.software.os.operating_system import OSRelease

from .ldap_account import LDAPAccount

if TYPE_CHECKING:
    from ..ldap_entry import LDAPEntry

class LDAPComputer(LDAPAccount, Computer):
    """A class to describe LDAP computer objects."""

    # ****************************************************************
    # Attributes & Constructors

    def __init__(self, ldap_entry: "LDAPEntry"):
        """
        Create a new instance of LDAPComputer.

        Args:
            ldap_entry (LDAPEntry): base dictionary entry
        """

        super().__init__(ldap_entry=ldap_entry)

        raw_os = self.entry.get("operatingSystem")
        raw_os_version = self.entry.get("operatingSystemVersion")

        # Retrieve OS and OS edition informations
        os_family_infos: str | None = OperatingSystem.get_matching_os_family(raw_os)
        os_release = None
        os_edition = None

        if os_family_infos is not None and raw_os_version is not None:
            os: OperatingSystem = OSOption[os_family_infos.replace(" ", "").upper()].value

            if len(os.releases) == 0:
                os.gen_releases()

            os_ver = os.__class__.find_version_in_str(raw_os_version)
            os_release = os.find_release(os_ver) if os_ver is not None else None
            os_edition_match: list[SoftwareEdition] = os.get_matching_editions(raw_os)

            if len(os_edition_match) != 0:
                os_edition = os_edition_match[0]

        self.hostname: str = self.entry.get("dNSHostName")

        # TODO: Handle SoftwareRelease and OSRelease

        Computer.__init__(
            self,
            computer_id=self.uuid,
            name=self._name,
            label=self.hostname,
            description=self.description,
            os_release=os_release,
            os_edition=os_edition,
        )

    # ****************************************************************
    # Methods

    def to_dict(self) -> dict[str, Any]:
        """Convert the current instance into a dictionary."""

        base_dict = super().to_dict()
        cpt_dict = Computer.to_dict(self)

        return {**base_dict, "hostname": cpt_dict.pop("label"), **cpt_dict}
