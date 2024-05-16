import os
from collections import defaultdict

from typing import Tuple, Dict


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

    @classmethod
    def load(cls, profile: str = None) -> 'Credentials':
        """
        Load credentials from the environment or a credentials file.
        :param profile: The desired profile from the credentials file (default profile is used if not specified).
        :return: A Credentials object.
        """
        try:
            return EnvironmentCredentials()
        except KeyError:
            return FileCredentials(profile)

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


class EnvironmentCredentials(Credentials):
    """
    Credentials loaded from environment variables. The following environment variables are used:
    - LARA_ACCESS_KEY_ID: The access key ID.
    - LARA_ACCESS_KEY_SECRET: The access key secret.
    """

    def __init__(self,
                 access_key_id_env: str = 'LARA_ACCESS_KEY_ID',
                 access_key_secret_env: str = 'LARA_ACCESS_KEY_SECRET'):
        access_key_id = os.getenv(access_key_id_env)
        access_key_secret = os.getenv(access_key_secret_env)

        if access_key_id is None or access_key_secret is None:
            raise KeyError(f'"{access_key_id_env}" and "{access_key_secret_env}" not found in environment')

        super().__init__(access_key_id, access_key_secret)


class FileCredentials(Credentials):
    """
    Credentials loaded from the credentials file ("~/.lara/credentials").
    """

    @staticmethod
    def __read_credentials_file(credentials_file: str) -> Dict[str, Tuple[str, str]]:
        with open(credentials_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        credentials = defaultdict(dict)

        profile = 'default'
        for line in lines:
            line = line.strip()
            if line.startswith('#'):
                continue
            if line.startswith('['):
                if not line.endswith(']'):
                    raise IOError(f'Invalid line in credentials file: {line}')
                profile = line[1:-1]
            elif '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                if key == 'lara_access_key_id':
                    credentials[profile]['lara_access_key_id'] = value.strip()
                elif key == 'lara_access_key_secret':
                    credentials[profile]['lara_access_key_secret'] = value.strip()
                else:
                    raise IOError(f'Invalid key in credentials file: {key}')
            else:
                raise IOError(f'Invalid line in credentials file: {line}')

        result = {}
        for profile, data in credentials.items():
            if 'lara_access_key_id' not in data:
                raise IOError(f'Missing "lara_access_key_id" for profile "{profile}": {credentials_file}')
            if 'lara_access_key_secret' not in data:
                raise IOError(f'Missing "lara_access_key_secret" for profile "{profile}": {credentials_file}')

            result[profile] = data['lara_access_key_id'], data['lara_access_key_secret']

        return result

    def __init__(self, profile: str = None, credentials_file: str = None):
        profile = profile or 'default'
        credentials_file = credentials_file or os.path.expanduser('~/.lara/credentials')

        if not os.path.isfile(credentials_file):
            raise FileNotFoundError(credentials_file)

        credentials = self.__read_credentials_file(credentials_file)
        if profile not in credentials:
            raise KeyError(f'Profile "{profile}" not found in credentials file: {credentials_file}')

        access_key_id, access_key_secret = credentials[profile]
        super().__init__(access_key_id, access_key_secret)
