"""A module that provide credential utilities."""

import getpass

import keyring
from keyring.credentials import Credential, SimpleCredential
from keyring.errors import KeyringError, PasswordDeleteError, PasswordSetError


class CredentialHelper:
    """A class that helps with credentials."""

    @staticmethod
    def save_credentials(service: str, username: str, password: str) -> None:
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

        try:
            keyring.set_password(service, username, password)

        except PasswordSetError as e:
            raise PasswordSetError(
                f"{__class__.__name__}.save_credentials::Error while saving credentials for {service}:{username}\n{e}"
            )

    @staticmethod
    def get_credentials(service: str) -> Credential | SimpleCredential:
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

        try:
            cred = keyring.get_credential(service, "")

            if cred is None:
                print(f"\nNo stored credentials for {service}. Please enter your credentials:")

                # Ask user's credentials
                username = input("Username: ")
                password = getpass.getpass("Password: ")

                # Saving credentials
                CredentialHelper.save_credentials(service, username, password)
                cred = SimpleCredential(username, password)

        except KeyringError as e:
            raise KeyringError(
                f"{__class__.__name__}.get_credentials::An error occured while retreiving credentials for {service}\n{e}"
            )

        return cred

    @staticmethod
    def del_credentials(service: str, username: str) -> None:
        """
        Remove stored credentials from the `keyring` using both the service identifier and the specified username.

        If the operation is successful, no value is returned. Otherwise, it will raise a `keyring.errors.PasswordDeleteError` if there's an issue deleting the password.

        Args:
            service (str) : The identifier for the service from which to delete credentials.
            username (str): The username whose associated credentials are to be deleted.

        Raises:
            keyring.errors.PasswordDeleteError: If there is an error while attempting to delete the password.
        """

        try:
            keyring.delete_password(service, username)

        except PasswordDeleteError as e:
            raise PasswordDeleteError(
                f"{__class__.__name__}.del_credentials::Error while deleting password for {service}:{username}\n{e}"
            )
