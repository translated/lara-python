class Credentials:
    """
    Credentials for accessing the Lara API. A credentials object has two properties:
    - access_key_id: The access key ID.
    - access_key_secret: The access key secret.

    IMPORTANT: Do not hard-code your access key ID and secret in your code. Always use environment variables or
    a credentials file. Please note also that the access key secret is never sent directly via HTTP, but it is used to
    sign the request. If you suspect that your access key secret has been compromised, you can revoke it in the Lara
    dashboard.
    """

    def __init__(self, access_key_id: str, access_key_secret: str):
        self._access_key_id: str = access_key_id
        self._access_key_secret: str = access_key_secret

    @property
    def access_key_id(self) -> str:
        """
        :return: The access key ID.
        """
        return self._access_key_id

    @property
    def access_key_secret(self) -> str:
        """
        :return: The access key secret.
        """
        return self._access_key_secret
