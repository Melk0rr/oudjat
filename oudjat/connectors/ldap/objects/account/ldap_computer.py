"""A module to handle manipulation of LDAP computer objects."""

from typing import TYPE_CHECKING, Dict, List

from oudjat.model.assets.computer import Computer
from oudjat.model.assets.software.os import OperatingSystem, OSOption
from oudjat.model.assets.software.software_edition import SoftwareEdition
from oudjat.model.assets.software.software_release import SoftwareReleaseDict

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

        # Retreive OS and OS edition informations
        os_family_infos: str = OperatingSystem.get_matching_os_family(raw_os)
        os_release = None
        os_edition = None

        if os_family_infos is not None and raw_os_version is not None:
            os: OperatingSystem = OSOption[os_family_infos.replace(" ", "").upper()].value

            if os is not None:
                if len(os.get_releases()) == 0:
                    os.gen_releases()

                os_ver = os.__class__.get_matching_version(raw_os_version)
                rel_search: SoftwareReleaseDict = os.find_release(os_ver)

                if len(rel_search) > 1:
                    rel_search = rel_search.find_rel_matching_label(os.get_name())

                os_release = next(iter(rel_search.values()))
                os_edition: List[SoftwareEdition] = os.get_matching_editions(raw_os)

                if os_edition is not None and len(os_edition) != 0:
                    os_edition = os_edition[0]

        self.hostname = self.entry.get("dNSHostName")

        Computer.__init__(
            self,
            computer_id=self.uuid,
            name=self.name,
            label=self.hostname,
            description=self.description,
            os_release=os_release,
            os_edition=os_edition,
        )

    # ****************************************************************
    # Methods

    def to_dict(self) -> Dict:
        """Convert the current instance into a dictionary."""

        base_dict = super().to_dict()
        cpt_dict = Computer.to_dict(self)

        return {**base_dict, "hostname": cpt_dict.pop("label"), **cpt_dict}
