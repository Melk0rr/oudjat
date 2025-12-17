"""Module to describe software release versions."""

import logging
import re
from enum import Enum
from typing import Any, NamedTuple, override

from oudjat.core.software.exceptions import (
    InvalidSoftwareVersionError,
)
from oudjat.utils import Context

from .definitions import STAGE_REG, VERSION_REG


class SoftwareReleaseStageProps(NamedTuple):
    """
    A helper class to handle stage property values.

    Attributes:
        qualifier (str): The stage quialifier
        value (int)    : The stage value
    """

    qualifier: str
    factor: int


class SoftwareReleaseStage(Enum):
    """
    An enumeration of software release stages.

    Along with major, minor and build version, a software version comes with a stage of development
    """

    ALPHA = SoftwareReleaseStageProps(qualifier="a", factor=0)
    BETA = SoftwareReleaseStageProps(qualifier="b", factor=1)
    RELEASE_CANDIDATE = SoftwareReleaseStageProps(qualifier="rc", factor=2)
    RELEASE = SoftwareReleaseStageProps(qualifier="r", factor=3)
    SERVICE_PACK = SoftwareReleaseStageProps(qualifier="sp", factor=4)

    @property
    def factor(self) -> int:
        """
        Return the stage factor.

        Returns:
            int: The factor value of the stage
        """

        return self._value_.factor

    @override
    def __str__(self) -> str:
        """
        Convert the SoftwareReleaseStage into a string.

        Returns:
            str: A string representation of the software release stage
        """

        return self._value_.qualifier

    @classmethod
    def from_qualifier(cls, qualifier: str) -> "SoftwareReleaseStage":
        """
        Return a SoftwareReleaseStage based on the provided qualifier.

        Args:
            qualifier (str): The qualifier of the stage

        Returns:
            SoftwareReleaseStage: The new stage based on the provided qualifier
        """

        def qualifier_cmp(stage: "SoftwareReleaseStage") -> bool:
            return str(stage) == qualifier

        return next(filter(qualifier_cmp, SoftwareReleaseStage))


class SoftwareReleaseVersion:
    """
    A class that describe and handle software release version.

    The class handles version stage and version semantic parts major, minor and build.
    """

    def __init__(
        self,
        version: int | str,
        stage: tuple["SoftwareReleaseStage", int] = (SoftwareReleaseStage.RELEASE, 1),
    ) -> None:
        """
        Create a new instance of SoftwareReleaseVersion.

        Args:
            version (int | str): initial version to set
            stage (tuple[SoftwareReleaseStage, int]): a tuple representing stage and stage version
        """

        self.logger: "logging.Logger" = logging.getLogger(__name__)
        context = Context()

        self._major: int = 0
        self._minor: int = 0
        self._build: int = 0

        self._stage: "SoftwareReleaseStage" = stage[0]
        self._stage_version: int = stage[1]
        self._raw: int | str = version

        if isinstance(version, int):
            self._major = version

        else:
            match = re.match(VERSION_REG, version)

            if match is None:
                raise InvalidSoftwareVersionError(f"{context}::Invalid version provided {version}")

            self._major = int(match.group(1))
            self._minor = int(match.group(2)) if match.group(2) is not None else 0
            self._build = int(match.group(3)) if match.group(3) is not None else 0

            self.logger.debug(
                f"{context}::New release version - {self._major}.{match.group(2)}.{match.group(3)} > {self._major}.{self._minor}.{self._build}"
            )

            if match.group(4) is not None:
                stage_match = re.match(STAGE_REG, match.group(4))

                if stage_match:
                    self._stage = SoftwareReleaseStage.from_qualifier(stage_match.group(1))
                    self._stage_version = int(stage_match.group(2))

    @property
    def major(self) -> int:
        """
        Return the major version number.

        Returns:
            int: major version number (default 0)
        """

        return self._major

    @major.setter
    def major(self, new_major: int) -> None:
        """
        Set the major version number of the current SoftwareReleaseVersion.

        Args:
            new_major (int): new major version value
        """

        self._major = new_major

    @property
    def minor(self) -> int:
        """
        Return the minor version number.

        Returns:
            int: minor version number (default 0)
        """

        return self._minor

    @minor.setter
    def minor(self, new_minor: int) -> None:
        """
        Set the minor version number of the current SoftwareReleaseVersion.

        Args:
            new_minor (int): new minor version value
        """

        self._minor = new_minor

    @property
    def build(self) -> int:
        """
        Return the build version number.

        Returns:
            int: build version number (default 0)
        """

        return self._build

    @build.setter
    def build(self, new_build: int) -> None:
        """
        Set the build version number of the current SoftwareReleaseVersion.

        Args:
            new_build (int): new build version value
        """

        self._build = new_build

    @property
    def raw(self) -> int | str:
        """
        Return the raw version value.

        Returns:
            int | str: raw version value
        """

        return self._raw

    @property
    def stage(self) -> "SoftwareReleaseStage":
        """
        Return the stage version.

        Returns:
            SoftwareReleaseStage: The current stage of the version
        """

        return self._stage

    @stage.setter
    def stage(self, new_stage: "SoftwareReleaseStage") -> None:
        """
        Set the stage of the current SoftwareReleaseVersion.

        Args:
            new_stage (SoftwareReleaseStage): New stage value
        """

        self._stage = new_stage

    @property
    def stage_version(self) -> int:
        """
        Return the stage version number.

        Returns:
            int: The current stage version of the version
        """

        return self._stage_version

    @stage_version.setter
    def stage_version(self, new_stage_version: int) -> None:
        """
        Set the stage version number of the current SoftwareReleaseVersion.

        Args:
            new_stage_version (int): New stage version value
        """

        self._stage_version = new_stage_version

    @property
    def values(self) -> tuple[int, int, int, int, int]:
        """
        Return a tuple of comparison values.

        Returns:
            tuple[int, int, int, int, int]: A tuple containing the values of the version that are used for comparison
        """

        return (
            self._major,
            self._minor,
            self._build,
            self._stage.factor,
            self._stage_version
        )

    def __gt__(self, other: "SoftwareReleaseVersion") -> bool:
        """
        Check if current version is above the other.

        Args:
            other (SoftwareReleaseVersion): The other version to compare

        Returns:
            bool: True if the current version is above the other. False otherwise
        """

        return self.values > other.values

    def __ge__(self, other: "SoftwareReleaseVersion") -> bool:
        """
        Check if current version is equal or above the other.

        Args:
            other (SoftwareReleaseVersion): The other version to compare

        Returns:
            bool: True if the current version is above or equal to the other. False otherwise
        """

        return self.values >= other.values

    def __lt__(self, other: "SoftwareReleaseVersion") -> bool:
        """
        Check if current version is below the other.

        Args:
            other (SoftwareReleaseVersion): The other version to compare

        Returns:
            bool: True if the current version is below the other. False otherwise
        """

        return self.values < other.values

    def __le__(self, other: "SoftwareReleaseVersion") -> bool:
        """
        Check if current version is equal or above the other.

        Args:
            other (SoftwareReleaseVersion): The other version to compare

        Returns:
            bool: True if the current version is lower or equal to the other. False otherwise
        """

        return self.values <= other.values

    @override
    def __eq__(self, other: object) -> bool:
        """
        Check if current version is equal to the other.

        Args:
            other (SoftwareReleaseVersion): The other version to compare

        Returns:
            bool: True if the current version equal to the other. False otherwise
        """

        if not isinstance(other, SoftwareReleaseVersion):
            raise ValueError(
                f"{Context()}::You are trying to compare a SoftwareReleaseVersion with {type(object)}"
            )

        return self.values == other.values

    @override
    def __ne__(self, other: object) -> bool:
        """
        Check if current version is different than the other.

        Args:
            other (SoftwareReleaseVersion): The other version to compare

        Returns:
            bool: True if the current version is different to the other. False otherwise
        """

        if not isinstance(other, SoftwareReleaseVersion):
            raise ValueError(
                f"{Context()}::You are trying to compare a SoftwareReleaseVersion with {type(object)}"
            )

        return self.values != other.values

    @override
    def __hash__(self) -> int:
        """
        Generate a hash for the current version.

        Returns:
            int: Hash based on the version numbers
        """

        return hash((self._major, self._minor, self._build, str(self._stage), self._stage_version))

    @override
    def __str__(self) -> str:
        """
        Convert the current SoftwareReleaseVersion into a string.

        Returns:
            str: a string representing the current software release version
        """

        base = f"{self._major}.{self._minor}.{self._build}"

        if not (self._stage == SoftwareReleaseStage.RELEASE and self._stage_version == 1):
            base += f"{self._stage}{self._stage_version}"

        return base

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the current software release version into a dictionary.

        Returns:
            dict[str, Any]: A dictionary representing the current instance
        """

        return {
            "raw": self._raw,
            "major": self._major,
            "minor": self._minor,
            "build": self._build,
            "stage": {
                "name": self._stage.name,
                "version": self._stage_version,
                "value": f"{self._stage}{self._stage_version}",
            },
        }
