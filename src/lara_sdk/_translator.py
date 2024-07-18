import time
from datetime import datetime
from enum import Enum
from typing import Optional, Union, List, Iterable, Callable

from gzip_stream import GZIPCompressedStream

from ._client import LaraObject, LaraClient
from ._credentials import Credentials
from ._errors import LaraApiError


# Objects --------------------------------------------------------------------------------------------------------------


class Memory(LaraObject):
    def __init__(self, **kwargs):
        self.id: str = kwargs.get('id')
        self.created_at: datetime = self._parse_date(kwargs.get('created_at', None))
        self.updated_at: datetime = self._parse_date(kwargs.get('updated_at', None))
        self.name: str = kwargs.get('name')
        self.external_id: Optional[str] = kwargs.get('external_id', None)
        self.secret: Optional[str] = kwargs.get('secret', None)
        self.owner_id: str = kwargs.get('owner_id')
        self.collaborators_count: int = kwargs.get('collaborators_count')
        self.shared_at: datetime = self._parse_date(kwargs.get('shared_at'))


class MemoryImport(LaraObject):
    def __init__(self, **kwargs):
        self.id: str = kwargs.get('id')
        self.begin: int = kwargs.get('begin')
        self.end: int = kwargs.get('end')
        self.channel: int = kwargs.get('channel')
        self.size: int = kwargs.get('size')
        self.progress: float = kwargs.get('progress')


class TextBlock(LaraObject):
    def __init__(self, **kwargs):
        self.text: str = kwargs.get('text')
        self.translatable: bool = kwargs.get('translatable', True)


class TextResult(LaraObject):
    def __init__(self, **kwargs):
        self.content_type: str = kwargs.get('content_type')
        self.source_language: str = kwargs.get('source_language')
        self.translation: Union[str, List[str], List[TextBlock]]
        self.adapted_to: Optional[List[str]] = kwargs.get('adapted_to', None)

        translation = kwargs.get('translation')

        if isinstance(translation, str):
            self.translation = translation
        elif isinstance(translation, list):
            if all(isinstance(e, str) for e in translation):
                self.translation = translation
            else:
                self.translation = [TextBlock(**e) for e in translation]


# Translator SDK -------------------------------------------------------------------------------------------------------


class Memories:
    def __init__(self, client: LaraClient):
        self._client: LaraClient = client
        self._polling_interval: int = 2

    def list(self) -> List[Memory]:
        return [Memory(**e) for e in self._client.get('/memories')]

    def create(self, name: str, external_id: str = None) -> Memory:
        return Memory(**self._client.post('/memories', {
            'name': name, 'external_id': external_id
        }))

    def get(self, id_: str) -> Optional[Memory]:
        try:
            return Memory(**self._client.get(f'/memories/{id_}'))
        except LaraApiError as e:
            if e.status_code == 404:
                return None
            raise

    def delete(self, id_: str) -> Memory:
        return Memory(**self._client.delete(f'/memories/{id_}'))

    def update(self, id_: str, name: str) -> Memory:
        return Memory(**self._client.put(f'/memories/{id_}', {
            'name': name
        }))

    def connect(self, ids: Union[str, List[str]]) -> Union[Optional[Memory], List[Memory]]:
        results = [Memory(**e) for e in self._client.post('/memories/connect', {
            'ids': ids if isinstance(ids, list) else [ids]
        })]

        if isinstance(ids, list):
            return results
        return results[0] if len(results) > 0 else None

    def import_tmx(self, id_: str, tmx: str) -> MemoryImport:
        with open(tmx, 'rb') as stream:
            compressed_stream = GZIPCompressedStream(stream, compression_level=7)
            return MemoryImport(**self._client.post(f'/memories/{id_}/import',
                                                    {'compression': 'gzip'}, {'tmx': compressed_stream}))

    def add_translation(self, id_: Union[str, List[str]], source: str, target: str, sentence: str, translation: str,
                        *, tuid: str = None, sentence_before: str = None, sentence_after: str = None) -> MemoryImport:
        body = {'source': source, 'target': target, 'sentence': sentence, 'translation': translation,
                'tuid': tuid, 'sentence_before': sentence_before, 'sentence_after': sentence_after}

        if isinstance(id_, list):
            body['ids'] = id_
            return MemoryImport(**self._client.put('/memories/content', body))
        return MemoryImport(**self._client.put(f'/memories/{id_}/content', body))

    def delete_translation(self, id_: Union[str, List[str]], source: str, target: str, sentence: str, translation: str,
                           *, tuid: str = None, sentence_before: str = None, sentence_after: str = None
                           ) -> MemoryImport:
        body = {'source': source, 'target': target, 'sentence': sentence, 'translation': translation,
                'tuid': tuid, 'sentence_before': sentence_before, 'sentence_after': sentence_after}

        if isinstance(id_, list):
            body['ids'] = id_
            return MemoryImport(**self._client.delete('/memories/content', body))
        return MemoryImport(**self._client.delete(f'/memories/{id_}/content', body))

    def get_import_status(self, id_: str) -> MemoryImport:
        return MemoryImport(**self._client.get(f'/memories/imports/{id_}'))

    def wait_for_import(self, memory_import: MemoryImport, *,
                        update_callback: Callable[[MemoryImport], None] = None,
                        max_wait_time: float = 0) -> MemoryImport:
        start = time.time()
        while memory_import.progress < 1.:
            if 0 < max_wait_time < time.time() - start:
                raise TimeoutError()

            time.sleep(self._polling_interval)

            memory_import = self.get_import_status(memory_import.id)
            if update_callback is not None:
                update_callback(memory_import)

        return memory_import


class TranslatePriority(Enum):
    NORMAL = 'normal'
    BACKGROUND = 'background'


class UseCache(Enum):
    YES = 'yes'
    NO = 'no'
    OVERWRITE = 'overwrite'


class Translator:
    def __init__(self, credentials: Credentials = None, *,
                 access_key_id: str = None, access_key_secret: str = None, server_url: str = None):
        if credentials is None:
            if access_key_id is not None and access_key_secret is not None:
                credentials = Credentials(access_key_id, access_key_secret)
            else:
                raise ValueError('either credentials or access_key_id and access_key_secret must be provided')

        self._client: LaraClient = LaraClient(credentials.access_key_id, credentials.access_key_secret, server_url)
        self.memories: Memories = Memories(self._client)

    def languages(self) -> List[str]:
        return self._client.get('/languages')

    def translate(self, text: Union[str, Iterable[str], Iterable[TextBlock]], *,
                  source: str = None, source_hint: str = None, target: str, adapt_to: List[str] = None,
                  instructions: List[str] = None, content_type: str = None,
                  multiline: bool = True, timeout_ms: int = None, priority: TranslatePriority = None,
                  use_cache: Union[bool, UseCache] = None, cache_ttl_s: int = None) -> TextResult:
        if isinstance(text, str):
            q = text
        elif hasattr(text, '__iter__'):
            if all(isinstance(e, str) for e in text):
                q = list(text)
            elif all(isinstance(e, TextBlock) for e in text):
                q = [e.__dict__ for e in text]
            else:
                raise ValueError('text must be an iterable of strings or TextBlock objects')
        else:
            raise ValueError('text must be a string or an iterable')

        if use_cache is True:
            use_cache = UseCache.YES
        elif use_cache is False:
            use_cache = UseCache.NO

        return TextResult(**self._client.post('/translate', {
            'source': source, 'target': target, 'source_hint': source_hint, 'content_type': content_type,
            'multiline': multiline, 'adapt_to': adapt_to, 'instructions': instructions, 'timeout': timeout_ms, 'q': q,
            'priority': priority.value if priority is not None else None,
            'use_cache': use_cache.value if use_cache is not None else None, 'cache_ttl': cache_ttl_s
        }))
