from decimal import Decimal

from cryptography.fernet import (
    Fernet,
    InvalidToken,
)

from django.conf import settings
from django.core.exceptions import (
    ImproperlyConfigured,
)
from django.db import models


PREFIX = "enc::"


def get_fernet():
    key = getattr(
        settings,
        "FIELD_ENCRYPTION_KEY",
        None,
    )

    if not key:
        raise ImproperlyConfigured(
            "FIELD_ENCRYPTION_KEY belum diset."
        )

    if isinstance(key, str):
        key = key.encode()

    return Fernet(key)


def encrypt_value(value):
    if value is None:
        return None

    value = str(value)

    # Hindari double encryption
    if value.startswith(PREFIX):
        return value

    encrypted = (
        get_fernet()
        .encrypt(value.encode())
        .decode()
    )

    return PREFIX + encrypted


def decrypt_value(value):
    if value is None:
        return None

    value = str(value)

    # Compatibility sementara untuk
    # data lama yang masih plaintext.
    if not value.startswith(PREFIX):
        return value

    token = value[len(PREFIX):]

    try:
        return (
            get_fernet()
            .decrypt(token.encode())
            .decode()
        )

    except InvalidToken:
        raise ValueError(
            "Data terenkripsi tidak valid "
            "atau FIELD_ENCRYPTION_KEY salah."
        )


class EncryptedCharField(models.TextField):

    def from_db_value(
        self,
        value,
        expression,
        connection,
    ):
        return decrypt_value(value)

    def to_python(self, value):
        if value is None:
            return None

        return decrypt_value(value)

    def get_prep_value(self, value):
        if value is None:
            return None

        return encrypt_value(value)


class EncryptedDecimalField(models.TextField):

    def from_db_value(
        self,
        value,
        expression,
        connection,
    ):
        if value is None:
            return None

        value = decrypt_value(value)

        return Decimal(str(value))

    def to_python(self, value):
        if value is None:
            return None

        if isinstance(value, Decimal):
            return value

        value = decrypt_value(value)

        return Decimal(str(value))

    def get_prep_value(self, value):
        if value is None:
            return None

        value = Decimal(str(value))

        return encrypt_value(
            format(value, "f")
        )