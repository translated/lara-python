import time
from datetime import datetime
from typing import Optional, Union, List, Dict, Iterator, Iterable, Callable

from gzip_stream import GZIPCompressedStream

from ._client import LaraObject, LaraClient, LaraError
from ._credentials import Credentials


# Objects --------------------------------------------------------------------------------------------------------------


class Memory(LaraObject):
    def __init__(self, data: Dict):
        self.id: str = data.get('id')
        self.created_at: datetime = self._parse_date(data.get('created_at', None))
        self.updated_at: datetime = self._parse_date(data.get('updated_at', None))
        self.name: str = data.get('name')
        self.external_id: Optional[str] = data.get('external_id', None)
        self.secret: Optional[str] = data.get('secret', None)
        self.owner_id: str = data.get('owner_id')
        self.collaborators_count: int = data.get('collaborators_count')
        self.shared_at: datetime = self._parse_date(data.get('shared_at'))


class MemoryImport(LaraObject):
    def __init__(self, data: Dict):
        self.id: str = data.get('id')
        self.begin: int = data.get('begin')
        self.end: int = data.get('end')
        self.channel: int = data.get('channel')
        self.size: int = data.get('size')
        self.progress: float = data.get('progress')


class TextResult(LaraObject):
    def __init__(self, data: Dict):
        self.content_type: str = data.get('content_type')
        self.source_language: str = data.get('source_language')
        self.translation: str = data.get('translation')
        self.adapted_to: Optional[List[str]] = data.get('adapted_to', None)


class DocumentResult(LaraObject):
    class Section(LaraObject):
        def __init__(self, data: Dict):
            self.text: str = data.get('text')
            self.translatable: bool = data.get('translatable', True)

    def __init__(self, data: Dict):
        self.content_type: str = data.get('content_type')
        self.source_language: str = data.get('source_language')
        self.translations: List[DocumentResult.Section] = [DocumentResult.Section(e) for e in data.get('translations')]
        self.adapted_to: Optional[List[str]] = data.get('adapted_to', None)

    def __iter__(self) -> Iterator['DocumentResult.Section']:
        return iter(self.translations)


class Document:
    class Section:
        def __init__(self, text: str, translatable: bool = True):
            self.text: str = text
            self.translatable: bool = translatable

        def __repr__(self):
            return self.__str__()

        def __str__(self):
            return f'Section(translatable={self.translatable}, "{self.text}")'

    def __init__(self, text: Union[str, Iterable[str]] = None):
        self._sections: List['Document.Section'] = []

        if text is not None:
            if isinstance(text, str):
                self.add_section(text)
            else:
                for item in text:
                    self.add_section(item)

    def __iter__(self) -> Iterator['Document.Section']:
        return iter(self._sections)

    def add_section(self, text: str, translatable: bool = True):
        self._sections.append(self.Section(text, translatable))

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return str(self._sections)


# Translator SDK -------------------------------------------------------------------------------------------------------


class LaraMemories:
    def __init__(self, client: LaraClient):
        self._client: LaraClient = client
        self._polling_interval: int = 2

    def list(self) -> List[Memory]:
        return [Memory(e) for e in self._client.get('/memories')]

    def create(self, name: str, external_id: str = None) -> Memory:
        return Memory(self._client.post('/memories', {
            'name': name, 'external_id': external_id
        }))

    def get(self, id_: str) -> Optional[Memory]:
        try:
            return Memory(self._client.get(f'/memories/{id_}'))
        except LaraError as e:
            if e.http_code == 404:
                return None
            raise

    def delete(self, id_: str) -> Memory:
        return Memory(self._client.delete(f'/memories/{id_}'))

    def update(self, id_: str, name: str) -> Memory:
        return Memory(self._client.put(f'/memories/{id_}', {
            'name': name
        }))

    def connect(self, ids: Union[str, List[str]]) -> Union[Optional[Memory], List[Memory]]:
        results = [Memory(e) for e in self._client.post('/memories/connect', {
            'ids': ids if isinstance(ids, list) else [ids]
        })]

        if isinstance(ids, list):
            return results
        return results[0] if len(results) > 0 else None

    def import_tmx(self, id_: str, tmx: str) -> MemoryImport:
        with open(tmx, 'rb') as stream:
            compressed_stream = GZIPCompressedStream(stream, compression_level=7)
            return MemoryImport(self._client.post(f'/memories/{id_}/import',
                                                  {'compression': 'gzip'}, {'tmx': compressed_stream}))

    def add_translation(self, id_: Union[str, List[str]], source: str, target: str, sentence: str, translation: str,
                        *, tuid: str = None, sentence_before: str = None, sentence_after: str = None) -> MemoryImport:
        body = {'source': source, 'target': target, 'sentence': sentence, 'translation': translation,
                'tuid': tuid, 'sentence_before': sentence_before, 'sentence_after': sentence_after}

        if isinstance(id_, list):
            body['ids'] = id_
            return MemoryImport(self._client.put('/memories/content', body))
        return MemoryImport(self._client.put(f'/memories/{id_}/content', body))

    def delete_translation(self, id_: Union[str, List[str]], source: str, target: str, sentence: str, translation: str,
                           *, tuid: str = None, sentence_before: str = None, sentence_after: str = None
                           ) -> MemoryImport:
        body = {'source': source, 'target': target, 'sentence': sentence, 'translation': translation,
                'tuid': tuid, 'sentence_before': sentence_before, 'sentence_after': sentence_after}

        if isinstance(id_, list):
            body['ids'] = id_
            return MemoryImport(self._client.delete('/memories/content', body))
        return MemoryImport(self._client.delete(f'/memories/{id_}/content', body))

    def get_import_status(self, id_: str) -> MemoryImport:
        return MemoryImport(self._client.get(f'/memories/imports/{id_}'))

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


class LaraTranslator:
    def __init__(self, credentials: Credentials = None, *,
                 access_key_id: str = None, access_key_secret: str = None, server_url: str = None):
        if credentials is None:
            if access_key_id is not None and access_key_secret is not None:
                credentials = Credentials(access_key_id, access_key_secret)
            else:
                credentials = Credentials.load()

        self._client: LaraClient = LaraClient(credentials.access_key_id, credentials.access_key_secret,
                                              base_url=server_url)
        self.memories: LaraMemories = LaraMemories(self._client)

    def languages(self) -> List[str]:
        return self._client.get('/languages')

    def translate(self, text: Union[str, Iterable[str]], *,
                  source: str = None, source_hint: str = None, target: str, adapt_to: List[str] = None,
                  instructions: List[str] = None, content_type: str = None,
                  multiline: bool = True, timeout_ms: int = None) -> Union[TextResult, List[TextResult]]:
        if isinstance(text, str):
            q = text
        elif hasattr(text, '__iter__'):
            q = list(text)
        else:
            raise ValueError('text must be a string or an iterable of strings')

        result = self._client.post('/translate', {
            'source': source, 'target': target, 'source_hint': source_hint, 'content_type': content_type,
            'multiline': multiline, 'adapt_to': adapt_to, 'instructions': instructions, 'timeout': timeout_ms, 'q': q
        })

        return [TextResult(item) for item in result] if isinstance(result, list) else TextResult(result)

    def translate_document(self, document: Document, *,
                           source: str = None, source_hint: str = None, target: str,
                           adapt_to: List[str] = None, instructions: List[str] = None,
                           content_type: str = None, multiline: bool = True, timeout_ms: int = None) -> DocumentResult:
        return DocumentResult(self._client.post('/translate/document', {
            'source': source, 'target': target, 'source_hint': source_hint, 'content_type': content_type,
            'multiline': multiline, 'adapt_to': adapt_to, 'instructions': instructions, 'timeout': timeout_ms,
            'q': [{'text': section.text, 'translatable': section.translatable} for section in document]
        }))
