"""A module that provide credential utilities."""

import getpass
import logging

import keyring
from keyring.credentials import SimpleCredential
from keyring.errors import KeyringError, PasswordDeleteError, PasswordSetError

from oudjat.utils.context import Context


class NoCredentialsError(ConnectionError):
    """
    A helper class to handle the absence of credentials.
    """

    def __init__(self, message: str) -> None:
        """
        Create a new instance of NoCredentialsError.

        Args:
            message (str): Error message
        """

        self.message: str = message
        super().__init__(self.message)


class InvalidCredentialsError(ConnectionError):
    """
    A helper class to handle the absence of credentials.
    """

    def __init__(self, message: str) -> None:
        """
        Create a new instance of NoCredentialsError.

        Args:
            message (str): Error message
        """

        self.message: str = message
        super().__init__(self.message)


class CredentialUtils:
    """A class that helps with credentials."""

    logger: "logging.Logger" = logging.getLogger(__name__)

    @classmethod
    def save_credentials(cls, service: str, username: str, password: str) -> None:
        """
        Use the `keyring` library to securely store the provided credentials (username and password) for a specified service in an encrypted vault.

        If the operation is successful, no value is returned. Otherwise, it will raise a `keyring.errors.PasswordSetError` if there's an issue setting the password.

        Args:
            service (str) : The identifier for the service or application where the credentials are being stored.
            username (str): The username to be associated with these credentials.
            password (str): The password that corresponds to the given username.

        Raises:
            keyring.errors.PasswordSetError: If there is an error while attempting to save the password.
        """

        context = Context()

        try:
            keyring.set_password(service, username, password)
            cls.logger.info(f"Successfully saved credentials for {service}")

        except PasswordSetError as e:
            raise PasswordSetError(
                f"{context}::Error while saving credentials for {service}:{username}\n{e}"
            )

    @classmethod
    def get_credentials(cls, service: str) -> "SimpleCredential":
        """
        Attempt to retrieve stored credentials from the `keyring` using the provided service name.

        If no credentials are found, it prompts the user to enter their username and password manually, which are then saved in the keyring before being returned. It also handles errors that may occur during
        retrieval or if there's an issue with the keyring itself by raising a `keyring.errors.KeyringError`.

        Args:
            service (str): The identifier for the service from which to retrieve credentials.

        Returns:
            keyring.credentials.SimpleCredential: An object containing the retrieved username and password.

        Raises:
            keyring.errors.KeyringError: If there is an error while retrieving the credentials or if the keyring operation fails.
        """

        context = Context()

        try:
            cred = keyring.get_credential(service, "")

            if cred is None:
                print(f"No stored credentials for {service}. Please enter your credentials:")

                # Ask user's credentials
                username = input("Username: ")
                password = getpass.getpass("Password: ")

                # Saving credentials
                CredentialUtils.save_credentials(service, username, password)
                cred = SimpleCredential(username, password)

            else:
                cred = SimpleCredential(cred.username, cred.password)

        except KeyringError as e:
            raise KeyringError(f"{context}::Could not retrieve credentials for {service}\n{e}")

        cls.logger.info(f"Retrieved credentials for {service}")
        return cred

    @classmethod
    def edit_credentials(cls, service: str, username: str) -> None:
        """
        Edit password for the provided service/username.

        Args:
            service (str) : The service for which the password will be edited
            username (str): The username for which the password will be edited
        """

        context = Context()

        try:
            if keyring.get_credential(service, username) is None:
                raise KeyringError(f"Could not find the provided service/username provided: {service}/{username}")

            password = getpass.getpass("Password: ")
            CredentialUtils.save_credentials(service, username, password)

        except KeyringError as e:
            raise KeyringError(f"{context}::Could not retrieve credentials for {service}\n{e}")

    @classmethod
    def del_credentials(cls, service: str, username: str) -> None:
        """
        Remove stored credentials from the `keyring` using both the service identifier and the specified username.

        If the operation is successful, no value is returned. Otherwise, it will raise a `keyring.errors.PasswordDeleteError` if there's an issue deleting the password.

        Args:
            service (str) : The identifier for the service from which to delete credentials.
            username (str): The username whose associated credentials are to be deleted.

        Raises:
            keyring.errors.PasswordDeleteError: If there is an error while attempting to delete the password.
        """

        context = Context()

        try:
            keyring.delete_password(service, username)
            cls.logger.info(f"Deleted credentials for {service}@{username}")

        except PasswordDeleteError as e:
            raise PasswordDeleteError(
                f"{context}::Error while deleting password for {service}@{username}\n{e}"
            )
