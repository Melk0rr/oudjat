"""
A helper module to handle mail sending.
"""

import logging
import mimetypes
import os
import re
import smtplib
from email.message import EmailMessage
from enum import Enum

from oudjat.utils.context import Context

EMAIL_REG = r"[^@ \t\r\n]+@[^@ \t\r\n]+\.[^@ \t\r\n]+"


class InvalidEmailAddressError(ValueError):
    """
    A helper class to handle invalid email format error.
    """

    def __init__(self, message: str) -> None:
        """
        Create a new instance of InvalidEmailError.

        Args:
            message (str): Error message
        """

        self.message: str = message
        super().__init__(self.message)

class EmptyMailRecipientError(ValueError):
    """
    A helper class to handle empty recipient errors.
    """

    def __init__(self, message: str) -> None:
        """
        Create a new instance of EmptyMailRecipientError.

        Args:
            message (str): Error message
        """

        self.message: str = message
        super().__init__(self.message)

class EmailSendError(ConnectionError):
    """
    A helper class to handle errors occuring when an email is sent.
    """

    def __init__(self, message: str) -> None:
        """
        Create a new instance of EmailSendError.

        Args:
            message (str): Error message
        """

        self.message: str = message
        super().__init__(self.message)


class MailRecipientType(Enum):
    """
    A helper enum that lists mail recipient types.

    """

    TO = "To"
    CC = "Cc"
    BCC = "Bcc"


class MailContentType(Enum):
    """
    A helper enum that lists content types.

    """

    PLAIN = "plain"
    HTML = "html"


class Mail:
    """
    A helper class to forge and send mails.
    """

    def __init__(self, smtp_server: str, smtp_port: int = 587) -> None:
        """
        Create a new mail.

        Attributes:
            smtp_server (str): The SMTP server to use
            smtp_port (int)  : The SMTP port used for the connection to the SMTP server
        """

        self.logger: "logging.Logger" = logging.getLogger(__name__)

        self._smtp_server: str = smtp_server
        self._smtp_port: int = smtp_port
        self._message: "EmailMessage" = EmailMessage()
        self._recipients: dict[str, list[str]] = {}

    @property
    def sender(self) -> str:
        """
        Return the email sender.

        Returns:
            str: The email sender
        """

        return self._message["From"]

    @sender.setter
    def sender(self, email: str) -> None:
        """
        Set the sender email.
        """

        if not re.match(EMAIL_REG, email):
            raise InvalidEmailAddressError(f"{Context()}::Invalid sender provided: {email}")

        self._message["From"] = email

    @property
    def subject(self) -> str:
        """
        Return the mail subject.

        Returns:
            str: Mail subject string
        """

        return self._message["Subject"]

    @subject.setter
    def subject(self, new_subject: str) -> None:
        """
        Set a new mail subject.

        Args:
            new_subject (str): New subject value
        """

        self._message["Subject"] = new_subject

    def add_recipient(
        self, email: str, recipient_type: "MailRecipientType" = MailRecipientType.TO
    ) -> None:
        """
        Add a new recipient to the mail.

        Args:
            email (str)                       : Email address of the recipient
            recipient_type (MailRecipientType): Recipient type
        """

        if re.match(EMAIL_REG, email):
            if recipient_type.value not in self._recipients.keys():
                self._recipients[recipient_type.value] = []

            self._recipients[recipient_type.value].append(email)

        else:
            self.logger.error(f"{Context()}::Invalid recipient provided {email}")

    def set_content(
        self, content: str, content_type: "MailContentType" = MailContentType.PLAIN
    ) -> None:
        """
        Set the email content.

        Args:
            content (str)                 : The content of the email
            content_type (MailContentType): The content type of the email (plain or html)
        """

        self._message.set_content(content, subtype=content_type.value)

    def add_attachment(self, filepath: str) -> None:
        """
        Add a file as email attachment.

        Args:
            filepath (str): The path of the file attachement
        """

        full_path = os.path.join(os.getcwd(), filepath)
        with open(full_path, "rb") as file:
            file_data = file.read()
            file_name = filepath.split("/")[-1]

        # Guess the content type based on file extension
        content_type, _ = mimetypes.guess_type(filepath)
        if content_type is None:
            content_type = "application/octet-stream"

        maintype, subtype = content_type.split("/", 1)
        self._message.add_attachment(
            file_data, maintype=maintype, subtype=subtype, filename=file_name
        )

    def send(self, username: str, password: str) -> bool:
        """
        Send the email.

        Args:
            username (str): The username used for the connection to the SMTP server
            password (str): The password used for the connection to the SMTP server
        """

        context = Context()

        if len(list(self._recipients.keys())) == 0:
            raise EmptyMailRecipientError(f"{context}::No mail recipient provided")

        for recipient_type in self._recipients.keys():
            self._message[recipient_type] = ", ".join(self._recipients[recipient_type])

        try:
            with smtplib.SMTP(self._smtp_server, self._smtp_port) as server:
                _ = server.starttls()
                _ = server.login(username, password)
                send = server.send_message(self._message)

                if send:
                    self.logger.error(
                        f"{context}::Some error occured while sending the email {send}"
                    )

        except smtplib.SMTPException as e:
            raise smtplib.SMTPException(f"{context}::{e}")

        return True
