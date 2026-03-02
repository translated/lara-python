import base64
import datetime
import hashlib
import hmac
import json
from typing import Dict, Optional, Union, List

import requests

from ._credentials import AccessKey, AuthToken
from ._errors import LaraApiError


class LaraObject:
    """
    This serves as a base class for all Lara API returned objects.
    """

    @staticmethod
    def _parse_date(date: Optional[str]) -> Optional[datetime.datetime]:
        if date is None:
            return None
        if date.endswith("Z"):
            date = date[:-1] + "+00:00"
        return datetime.datetime.fromisoformat(date) if date is not None else None

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        result = f"{self.__class__.__name__}("
        for name, value in self.__dict__.items():
            if isinstance(value, datetime.datetime):
                value = value.isoformat()
            if isinstance(value, str):
                value = f'"{value}"'
            result += f"{name}={value}, "

        return result[:-2] + ")"



class LaraClient:
    """
    This class is used to interact with Lara via the REST API with JWT authentication support.
    """

    def __init__(self, auth: Union[AccessKey, AuthToken], server_url: str = None):
        """
        Initialize the Lara client with authentication.

        :param auth: Authentication method (AccessKey or AuthToken)
        :param server_url: Optional custom server URL (defaults to https://api.laratranslate.com)
        """
        self.base_url: str = (server_url or 'https://api.laratranslate.com').strip().rstrip('/')
        self.sdk_name: str = 'lara-python'
        self.sdk_version: str = __import__('lara_sdk').__version__

        # Authentication state
        self._auth: Union[AccessKey, AuthToken] = auth
        self._token: Optional[str] = None
        self._refresh_token: Optional[str] = None

        # If AuthToken is provided, use it immediately
        if isinstance(auth, AuthToken):
            self._token = auth.token
            self._refresh_token = auth.refresh_token

        self.session: requests.Session = requests.Session()

    def get(self, path: str, params: Dict = None, headers: Dict = None) -> Optional[Union[Dict, List, bytes]]:
        """
        Sends a GET request to the Lara API.
        :param path: The path to send the request to.
        :param params: The parameters to send with the request.
        :param headers: Additional headers to include in the request.
        :return: The JSON response from the API.
        """
        return self._request('GET', path, body=params, headers=headers)

    def delete(self, path: str, params: Dict = None, headers: Dict = None) -> Optional[Union[Dict, List, bytes]]:
        """
        Sends a DELETE request to the Lara API.
        :param path: The path to send the request to.
        :param params: The parameters to send with the request.
        :param headers: Additional headers to include in the request.
        :return: The JSON response from the API.
        """
        return self._request('DELETE', path, body=params, headers=headers)

    def post(self, path: str, body: Dict = None, files: Dict = None, headers: Dict = None) -> Optional[Union[Dict, List, bytes]]:
        """
        Sends a POST request to the Lara API.
        :param path: The path to send the request to.
        :param body: The parameters to send with the request.
        :param files: The files to send with the request. If present, request will be sent as multipart/form-data.
        :param headers: Additional headers to include in the request.
        :return: The JSON response from the API.
        """
        return self._request('POST', path, body, files, headers)

    def put(self, path: str, body: Dict = None, files: Dict = None, headers: Dict = None) -> Optional[Union[Dict, List, bytes]]:
        """
        Sends a PUT request to the Lara API.
        :param path: The path to send the request to.
        :param body: The parameters to send with the request.
        :param files: The files to send with the request. If present, request will be sent as multipart/form-data.
        :param headers: Additional headers to include in the request.
        :return: The JSON response from the API.
        """
        return self._request('PUT', path, body, files, headers)

    def post_and_get_stream(self, path: str, body: Dict = None, files: Dict = None, headers: Dict = None):
        """
        Sends a POST request to the Lara API and yields streaming responses.
        :param path: The path to send the request to.
        :param body: The parameters to send with the request.
        :param files: The files to send with the request. If present, request will be sent as multipart/form-data.
        :param headers: Additional headers to include in the request.
        :return: A generator yielding streaming responses.
        """
        return self._request_stream('POST', path, body, files, headers)

    def _request(self, method: str, path: str, body: Dict = None, files: Dict = None, headers: Dict = None,
                 retry_count: int = 0) -> Optional[Union[Dict, List, bytes]]:
        """
        Execute an authenticated HTTP request with automatic token management.
        """
        # Ensure we have a valid token
        if self._token is None:
            self._authenticate()

        if not path.startswith('/'):
            path = '/' + path

        _headers = {
            'Date': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'X-Lara-SDK-Name': self.sdk_name,
            'X-Lara-SDK-Version': self.sdk_version,
            'Authorization': f'Bearer {self._token}'
        }

        # Add custom headers
        if headers is not None:
            _headers.update(headers)

        if body is not None:
            body = {k: v for k, v in body.items() if v is not None}

        if files is not None:
            response = self.session.request(method, f'{self.base_url}{path}', headers=_headers, data=body, files=files)
        elif method == 'GET':
            response = self.session.request(method, f'{self.base_url}{path}', headers=_headers, params=body)
        else:
            response = self.session.request(method, f'{self.base_url}{path}', headers=_headers, json=body)

        # Handle successful responses
        if 200 <= response.status_code < 300:
            if response.status_code == 204:
                return None
            if "text/csv" in response.headers.get('Content-Type', '') or "image/" in response.headers.get('Content-Type', ''):
                return response.content
            try:
                data = response.json()

                # Backward compatibility
                if isinstance(data, dict) and 'content' in data:
                    return data['content']

                return data
            except:
                return None

        # Handle 401 - token expired, refresh and retry once
        if response.status_code == 401 and retry_count < 1:
            self._token = None
            return self._request(method, path, body, files, headers, retry_count=retry_count + 1)

        raise LaraApiError.from_response(response)

    def _request_stream(self, method: str, path: str, body: Dict = None, files: Dict = None, headers: Dict = None,
                        retry_count: int = 0):
        # Ensure we have a valid token
        if self._token is None:
            self._authenticate()

        if not path.startswith('/'):
            path = '/' + path

        _headers = {
            'Date': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'X-Lara-SDK-Name': self.sdk_name,
            'X-Lara-SDK-Version': self.sdk_version,
            'Authorization': f'Bearer {self._token}'
        }

        if headers is not None:
            _headers.update(headers)

        if body is not None:
            body = {k: v for k, v in body.items() if v is not None}

        if files is not None:
            response = self.session.request(method, f'{self.base_url}{path}', headers=_headers, data=body, files=files, stream=True)
        else:
            response = self.session.request(method, f'{self.base_url}{path}', headers=_headers, json=body, stream=True)

        if not (200 <= response.status_code < 300):
            # Handle 401 - token expired, refresh and retry once
            if response.status_code == 401 and retry_count < 1:
                self._token = None
                yield from self._request_stream(method, path, body, files, headers, retry_count=retry_count + 1)
                return

            raise LaraApiError.from_response(response)

        for line in response.iter_lines(decode_unicode=True):
            if line:
                try:
                    parsed = json.loads(line)
                    data = parsed.get('data', parsed)
                    if isinstance(data, dict) and 'content' in data:  # backward compatibility
                        yield data['content']
                    else:
                        yield data
                except (json.JSONDecodeError, AttributeError):
                    pass

    def _authenticate(self) -> str:
        """
        Authenticate using AccessKey or AuthToken to obtain JWT tokens.

        This method is protected to enable internal token extraction for company use.
        External SDK users should not call this method directly.

        :return: The JWT access token string
        """
        # If we already have a token, return it
        if self._token is not None:
            return self._token

        if self._refresh_token is not None:
            # Try to refresh first
            self._refresh()
        elif isinstance(self._auth, AuthToken):
            self._token = self._auth.token
            self._refresh_token = self._auth.refresh_token
        elif isinstance(self._auth, AccessKey):
            self._authenticate_with_access_key()
        else:
            raise ValueError(f'Invalid authentication type: {type(self._auth).__name__}')

        return self._token

    def _authenticate_with_access_key(self) -> None:
        """Authenticate using AccessKey with challenge-response."""
        path = '/v2/auth'
        method = 'POST'
        date = datetime.datetime.now(datetime.timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT')
        content_type = 'application/json'

        body = {'id': self._auth.id}
        body_string = json.dumps(body, ensure_ascii=False, separators=(',', ':'))
        body_bytes = body_string.encode('UTF-8')

        content_md5 = base64.b64encode(hashlib.md5(body_bytes).digest()).decode('UTF-8')
        challenge = self._compute_signature(
            self._auth.secret,
            method,
            path,
            content_md5,
            content_type,
            date
        )

        headers = {
            'Authorization': f'Lara:{challenge}',
            'X-Lara-Date': date,
            'Content-Type': content_type,
            'Content-MD5': content_md5,
            'X-Lara-SDK-Name': self.sdk_name,
            'X-Lara-SDK-Version': self.sdk_version
        }

        response = self.session.post(f'{self.base_url}{path}', headers=headers, data=body_string)

        if 200 <= response.status_code < 300:
            data = response.json()
            self._token = data.get('token')
            self._refresh_token = response.headers.get('x-lara-refresh-token')

            if not self._token or not self._refresh_token:
                raise LaraApiError(500, "AuthenticationError", "Missing token or refresh token in authentication response")
        else:
            raise LaraApiError.from_response(response)

    def _refresh(self) -> None:
        """Refresh JWT token using the refresh token."""
        path = '/v2/auth/refresh'

        headers = {
            'Authorization': f'Bearer {self._refresh_token}',
            'X-Lara-Date': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'X-Lara-SDK-Name': self.sdk_name,
            'X-Lara-SDK-Version': self.sdk_version
        }

        response = self.session.post(f'{self.base_url}{path}', headers=headers)

        if 200 <= response.status_code < 300:
            data = response.json()
            self._token = data.get('token')

            # Update refresh token if a new one is provided
            new_refresh_token = response.headers.get('x-lara-refresh-token')
            if new_refresh_token:
                self._refresh_token = new_refresh_token

            if not self._token:
                raise LaraApiError(500, "AuthenticationError", "Missing token in refresh response")
        else:
            # Refresh failed, raise the error
            raise LaraApiError.from_response(response)

    def _compute_signature(self, secret: str, method: str, path: str, content_md5: str,
                          content_type: str, date: str) -> str:
        """Compute HMAC-SHA256 signature for challenge-response authentication."""
        challenge = f'{method}\n{path}\n{content_md5}\n{content_type}\n{date}'
        secret_bytes = secret.encode('UTF-8')
        challenge_bytes = challenge.encode('UTF-8')

        signature = hmac.new(secret_bytes, challenge_bytes, hashlib.sha256).digest()
        return base64.b64encode(signature).decode('UTF-8')
