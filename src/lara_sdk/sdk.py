import base64
import datetime
import hashlib
import hmac
import json
import os
import time
from typing import List, Dict, Union, Optional, Callable

import requests
from gzip_stream import GZIPCompressedStream

from .models import Memory, MemoryImport, Document


class Credentials(object):
    @classmethod
    def auto(cls):
        # search in ENV
        access_key_id = os.getenv("LARA_ACCESS_KEY_ID")
        access_key_secret = os.getenv("LARA_ACCESS_KEY_SECRET")

        if access_key_id is None or access_key_secret is None:
            raise KeyError("LARA_ACCESS_KEY_ID and LARA_ACCESS_KEY_SECRET not found in ENV")

        return cls(access_key_id, access_key_secret)

    def __init__(self, access_key_id, access_key_secret):
        self.access_key_id = access_key_id
        self.access_key_secret = access_key_secret


class LaraError(Exception):
    @classmethod
    def from_response(cls, response):
        body = response.json()
        error = body.get("error", {})
        name = error.get("type", "UnknownError")
        message = error.get("message", "An unknown error occurred")

        return cls(response.status_code, name, message)

    def __init__(self, http_code, name, message):
        super().__init__(f"(HTTP {http_code}) {name}: {message}")

        self.http_code = http_code
        self.name = name
        self.message = message


class _SignedSession(requests.Session):
    def __init__(self, access_key_id: str, access_key_secret: str):
        super().__init__()
        self.access_key_id = access_key_id
        self.access_key_secret = access_key_secret

    def prepare_request(self, request: requests.Request) -> requests.PreparedRequest:
        result = super().prepare_request(request)
        if self.access_key_id is not None and self.access_key_secret is not None:
            result.headers["Authorization"] = f"Lara {self.access_key_id}:{self._sign(result)}"
        return result

    def _sign(self, request: requests.PreparedRequest) -> str:
        date = request.headers.get("Date")
        content_md5 = request.headers.get("Content-MD5", "")
        content_type = request.headers.get("Content-Type", "")
        method = request.headers.get("X-HTTP-Method-Override", request.method)
        path = request.path_url

        raw = f"{method}\n{path}\n{content_md5}\n{content_type}\n{date}".encode("UTF-8")
        secret = self.access_key_secret.encode("UTF-8")

        signature = hmac.new(secret, raw, hashlib.sha1).digest()
        return base64.b64encode(signature).decode("UTF-8")


class _LaraClient(object):
    def __init__(self, credentials: Credentials, base_url: str = "http://localhost:8000"):
        from . import __version__

        self.base_url = base_url
        self.access_key_id = credentials.access_key_id
        self.access_key_secret = credentials.access_key_secret
        self.sdk_name = "lara-python"
        self.sdk_version = __version__

    def get(self, path: str, params: Dict = None) -> Optional[Union[Dict, List]]:
        return self._request("GET", path, body=params)

    def delete(self, path: str, params: Dict = None) -> Optional[Union[Dict, List]]:
        return self._request("DELETE", path, body=params)

    def post(self, path: str, body: Dict = None, files: Dict = None) -> Optional[Union[Dict, List]]:
        return self._request("POST", path, body, files)

    def put(self, path: str, body: Dict = None, files: Dict = None) -> Optional[Union[Dict, List]]:
        return self._request("PUT", path, body, files)

    def _request(self, method: str, path: str, body: Dict = None, files: Dict = None) -> Optional[Union[Dict, List]]:
        if not path.startswith("/"):
            path = "/" + path

        headers = {
            "X-HTTP-Method-Override": method,
            "Date": datetime.datetime.now(datetime.timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000"),
            "X-Lara-SDK-Name": self.sdk_name,
            "X-Lara-SDK-Version": self.sdk_version
        }

        if body is not None:
            body = {k: v for k, v in body.items() if v is not None}

            if len(body) > 0:
                encoded_body = json.dumps(body, ensure_ascii=False, separators=(",", ":")).encode("UTF-8")
                headers["Content-MD5"] = hashlib.md5(encoded_body).hexdigest()

        with _SignedSession(self.access_key_id, self.access_key_secret) as session:
            if files is not None:
                response = session.request("POST", f"{self.base_url}{path}", headers=headers, data=body, files=files)
            else:
                response = session.request("POST", f"{self.base_url}{path}", headers=headers, json=body)

        if response.status_code != requests.codes.ok:
            raise LaraError.from_response(response)
        return response.json().get("content", None)


class MemoryAPI(object):
    def __init__(self, client: _LaraClient):
        self._client = client
        self._polling_interval_step = 1
        self._max_polling_interval = 3

    def list(self) -> List[Memory]:
        return Memory.parse(self._client.get("/memories"))

    def create(self, name: str, external_id: str = None) -> Memory:
        return Memory.parse(self._client.post("/memories", {
            "name": name, "external_id": external_id
        }))

    def get(self, id: str) -> Optional[Memory]:
        try:
            return Memory.parse(self._client.get(f"/memories/{id}"))
        except LaraError as e:
            if e.http_code == 404:
                return None
            raise

    def delete(self, id: str) -> Memory:
        return Memory.parse(self._client.delete(f"/memories/{id}"))

    def update(self, id: str, name: str) -> Memory:
        return Memory.parse(self._client.put(f"/memories/{id}", {
            "name": name
        }))

    def connect(self, ids: Union[str, List[str]]) -> Union[Optional[Memory], List[Memory]]:
        results = Memory.parse(self._client.post("/memories/connect", {
            "ids": ids if isinstance(ids, list) else [ids]
        }))

        if isinstance(ids, list):
            return results
        else:
            return results[0] if len(results) > 0 else None

    def import_tmx(self, id: str, tmx: str) -> MemoryImport:
        with open(tmx, "rb") as stream:
            compressed_stream = GZIPCompressedStream(stream, compression_level=7)
            return MemoryImport.parse(self._client.post(f"/memories/{id}/import",
                                                        {"compression": "gzip"}, {"tmx": compressed_stream}))

    def add_translation(self, id: Union[str, List[str]], source: str, target: str, sentence: str, translation: str,
                        tuid: str = None, sentence_before: str = None, sentence_after: str = None) -> MemoryImport:
        body = {"source": source, "target": target, "sentence": sentence, "translation": translation,
                "tuid": tuid, "sentence_before": sentence_before, "sentence_after": sentence_after}

        if isinstance(id, list):
            body["ids"] = id
            return MemoryImport.parse(self._client.put("/memories/content", body))
        else:
            return MemoryImport.parse(self._client.put(f"/memories/{id}/content", body))

    def delete_translation(self, id: Union[str, List[str]], source: str, target: str, sentence: str, translation: str,
                           tuid: str = None, sentence_before: str = None, sentence_after: str = None) -> MemoryImport:
        body = {"source": source, "target": target, "sentence": sentence, "translation": translation,
                "tuid": tuid, "sentence_before": sentence_before, "sentence_after": sentence_after}

        if isinstance(id, list):
            body["ids"] = id
            return MemoryImport.parse(self._client.delete("/memories/content", body))
        else:
            return MemoryImport.parse(self._client.delete(f"/memories/{id}/content", body))

    def _get_import(self, id: str) -> MemoryImport:
        return MemoryImport.parse(self._client.get(f"/memories/imports/{id}"))

    def wait_for(self, import_job: Union[str, MemoryImport], max_secs: int = 0,
                 callback: Callable[[MemoryImport], None] = None) -> MemoryImport:
        id = import_job.id if isinstance(import_job, MemoryImport) else import_job

        start = time.time()
        interval = self._polling_interval_step
        while True:
            import_status = self._get_import(id)
            if callback is not None:
                callback(import_status)

            if import_status.progress == 1:
                return import_status

            if max_secs > 0 and (time.time() - start > max_secs):
                raise TimeoutError("Import job did not finish in time")

            time.sleep(interval)
            interval = min(interval * 2, self._max_polling_interval)


class TranslateOptions(object):
    def __init__(self, adapt_to: List[str] = None, instructions: List[str] = None,
                 content_type: str = None, multiline: bool = True, timeout: int = None, source_hint: str = None):
        self.adapt_to: List[str] = adapt_to
        self.multiline: bool = multiline
        self.content_type: str = content_type
        self.instructions: List[str] = instructions
        self.timeout: int = timeout
        self.source_hint: str = source_hint


class Lara(object):
    def __init__(self, credentials: Credentials = None):
        if credentials is None:
            credentials = Credentials.auto()

        self._client = _LaraClient(credentials)
        self.memories: MemoryAPI = MemoryAPI(self._client)

    def languages(self) -> List[str]:
        return self._client.get("/languages")

    def translate(self, source: Optional[str], target: str, text: Union[str, List[str], Document],
                  options: TranslateOptions = None) -> Union[str, List[str], Document]:
        if isinstance(text, Document):
            q = text
        else:
            q = Document.wrap(text)

        request = {
            "source": source,
            "target": target,
        }

        if options is not None:
            request.update({k: v for k, v in options.__dict__.items() if v is not None})

        if q.content_type is not None:
            request["content_type"] = q.content_type

        request["q"] = [{k: v for k, v in section.__dict__.items() if v is not None} for section in q.sections]

        translation = Document.parse(self._client.get("/translate", request))
        if isinstance(text, Document):
            return translation

        translations: List[str] = [section.text for section in translation.sections]
        if isinstance(text, list):
            return translations
        else:
            return translations[0] if len(translations) > 0 else None
