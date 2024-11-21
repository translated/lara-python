import base64
import datetime
import hashlib
import hmac
import json
from typing import Dict, Optional, Union, List

import requests

from ._errors import LaraApiError


class _SignedSession(requests.Session):
    def __init__(self, access_key_id: str, access_key_secret: str):
        super().__init__()
        self.access_key_id = access_key_id
        self.access_key_secret = access_key_secret

    def prepare_request(self, request: requests.Request) -> requests.PreparedRequest:
        result = super().prepare_request(request)
        if self.access_key_id is not None and self.access_key_secret is not None:
            result.headers['Authorization'] = f'Lara {self.access_key_id}:{self._sign(result)}'
        return result

    def _sign(self, request: requests.PreparedRequest) -> str:
        date = request.headers.get('Date').strip()
        content_md5 = request.headers.get('Content-MD5', '').strip()
        content_type = request.headers.get('Content-Type', '').split(';', 1)[0].strip()
        method = request.headers.get('X-HTTP-Method-Override', request.method).strip().upper()
        path = request.path_url

        raw = f'{method}\n{path}\n{content_md5}\n{content_type}\n{date}'.encode('UTF-8')
        secret = self.access_key_secret.encode('UTF-8')

        signature = hmac.new(secret, raw, hashlib.sha256).digest()
        return base64.b64encode(signature).decode('UTF-8')


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
    This class is used to interact with Lara via the REST API.
    """

    def __init__(self, access_key_id: str, access_key_secret: str, server_url: str = None):
        self.base_url: str = (server_url or 'https://api.laratranslate.com').strip().rstrip('/')
        self.session: _SignedSession = _SignedSession(access_key_id, access_key_secret)
        self.sdk_name: str = 'lara-python'
        self.sdk_version: str = __import__('lara_sdk').__version__

    def get(self, path: str, params: Dict = None) -> Optional[Union[Dict, List]]:
        """
        Sends a GET request to the Lara API.
        :param path: The path to send the request to.
        :param params: The parameters to send with the request.
        :return: The JSON response from the API.
        """
        return self._request('GET', path, body=params)

    def delete(self, path: str, params: Dict = None) -> Optional[Union[Dict, List]]:
        """
        Sends a DELETE request to the Lara API.
        :param path: The path to send the request to.
        :param params: The parameters to send with the request.
        :return: The JSON response from the API.
        """
        return self._request('DELETE', path, body=params)

    def post(self, path: str, body: Dict = None, files: Dict = None) -> Optional[Union[Dict, List]]:
        """
        Sends a POST request to the Lara API.
        :param path: The path to send the request to.
        :param body: The parameters to send with the request.
        :param files: The files to send with the request. If present, request will be sent as multipart/form-data.
        :return: The JSON response from the API.
        """
        return self._request('POST', path, body, files)

    def put(self, path: str, body: Dict = None, files: Dict = None) -> Optional[Union[Dict, List]]:
        """
        Sends a PUT request to the Lara API.
        :param path: The path to send the request to.
        :param body: The parameters to send with the request.
        :param files: The files to send with the request. If present, request will be sent as multipart/form-data.
        :return: The JSON response from the API.
        """
        return self._request('PUT', path, body, files)

    def _request(self, method: str, path: str, body: Dict = None, files: Dict = None) -> Optional[Union[Dict, List]]:
        if not path.startswith('/'):
            path = '/' + path

        headers = {
            'X-HTTP-Method-Override': method,
            'Date': datetime.datetime.now(datetime.timezone.utc).strftime('%a, %d %b %Y %H:%M:%S +0000'),
            'X-Lara-SDK-Name': self.sdk_name,
            'X-Lara-SDK-Version': self.sdk_version
        }

        if body is not None:
            body = {k: v for k, v in body.items() if v is not None}

            if len(body) > 0:
                encoded_body = json.dumps(body, ensure_ascii=False, separators=(',', ':')).encode('UTF-8')
                headers['Content-MD5'] = hashlib.md5(encoded_body).hexdigest()

        if files is not None:
            response = self.session.request('POST', f'{self.base_url}{path}', headers=headers, data=body, files=files)
        else:
            response = self.session.request('POST', f'{self.base_url}{path}', headers=headers, json=body)

        if 200 <= response.status_code < 300:
            return response.json().get('content', None)
        raise LaraApiError.from_response(response)
