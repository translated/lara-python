import warnings
from typing import Optional


class AccessKey:
    """
    Access key authentication for the Lara API.

    An AccessKey has two properties:
    - id: The access key ID.
    - secret: The access key secret.

    IMPORTANT: Do not hard-code your access key ID and secret in your code. Always use environment variables or
    a credentials file. The access key secret is used to generate a challenge signature for authentication.
    """

    def __init__(self, id: str, secret: str):
        """
        Initialize an AccessKey.

        :param id: The access key ID.
        :param secret: The access key secret.
        """
        self._id: str = id
        self._secret: str = secret

    @property
    def id(self) -> str:
        """
        :return: The access key ID.
        """
        return self._id

    @property
    def secret(self) -> str:
        """
        :return: The access key secret.
        """
        return self._secret

    @property
    def access_key_id(self) -> str:
        """
        .. deprecated:: 1.7.0
            Use :attr:`id` instead.

        :return: The access key ID.
        """
        return self._id

    @property
    def access_key_secret(self) -> str:
        """
        .. deprecated:: 1.7.0
            Use :attr:`secret` instead.

        :return: The access key secret.
        """
        return self._secret


class AuthToken:
    """
    Pre-authenticated token for the Lara API.

    An AuthToken has two properties:
    - token: The JWT access token.
    - refresh_token: The JWT refresh token.

    Use this class when you already have a valid JWT token and refresh token,
    for example from a previous authentication or from another authentication service.
    """

    def __init__(self, token: str, refresh_token: str):
        """
        Initialize an AuthToken.

        :param token: The JWT access token.
        :param refresh_token: The JWT refresh token.
        """
        self._token: str = token
        self._refresh_token: str = refresh_token

    @property
    def token(self) -> str:
        """
        :return: The JWT access token.
        """
        return self._token

    @property
    def refresh_token(self) -> str:
        """
        :return: The JWT refresh token.
        """
        return self._refresh_token


class Credentials(AccessKey):
    """
    .. deprecated:: 1.7.0
        Use :class:`AccessKey` instead.

    Legacy credentials class for backward compatibility.
    This class extends AccessKey and provides deprecated getter methods.
    Will be removed in a future version.
    """

    def __init__(self, access_key_id: Optional[str] = None, access_key_secret: Optional[str] = None):
        """
        Initialize Credentials (deprecated).

        .. deprecated:: 1.7.0
            Use :class:`AccessKey` instead with parameters ``id`` and ``secret``.

        :param access_key_id: The access key ID.
        :param access_key_secret: The access key secret.
        """
        warnings.warn(
            "Credentials is deprecated, use AccessKey instead",
            DeprecationWarning,
            stacklevel=2
        )
        super().__init__(access_key_id, access_key_secret)
