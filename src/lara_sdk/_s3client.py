from typing import IO, TypedDict
import requests

class S3UploadFields(TypedDict):
    acl: str
    bucket: str
    key: str


class S3Client():
    def __init__(self):
        self._session = requests.Session()

    def upload(self, url: str, fields: S3UploadFields, file_payload: IO[bytes]) -> None:
        files_dict = {'file': file_payload}

        data_fields = {key: str(value) for key, value in fields.items()}

        try:
            response = self._session.post(url, data=data_fields, files=files_dict)
            
            response.raise_for_status()
        except requests.RequestException as e:
            raise e

    def download(self, url: str) -> bytes:
        try:
            response = self._session.get(url)
            response.raise_for_status()
            return response.content
        except requests.RequestException as e:
            raise e

