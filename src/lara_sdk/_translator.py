import time
from datetime import datetime
from enum import Enum
from typing import Optional, Union, List, Iterable, Callable, Literal, Dict
from dataclasses import dataclass
import mimetypes
from pathlib import Path
import json

from gzip_stream import GZIPCompressedStream

from ._client import LaraObject, LaraClient
from ._credentials import Credentials, AccessKey, AuthToken
from ._errors import LaraApiError
from ._s3client import S3Client, S3UploadFields

TranslationStyle = Literal["faithful", "fluid", "creative"]
GlossaryFileFormat = Literal["csv/table-uni", "csv/table-multi"]

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

class Glossary(LaraObject):
    def __init__(self, **kwargs):
        self.id: str = kwargs.get('id')
        self.name: str = kwargs.get('name')
        self.owner_id: str = kwargs.get('owner_id')
        self.created_at: datetime = self._parse_date(kwargs.get('created_at', None))
        self.updated_at: datetime = self._parse_date(kwargs.get('updated_at', None))

class GlossaryImport(LaraObject):
    def __init__(self, **kwargs):
        self.id: str = kwargs.get('id')
        self.begin: int = kwargs.get('begin')
        self.end: int = kwargs.get('end')
        self.channel: int = kwargs.get('channel')
        self.size: int = kwargs.get('size')
        self.progress: float = kwargs.get('progress')

class GlossaryCounts(LaraObject):
    def __init__(self, **kwargs):
        self.unidirectional: Optional[Dict[str, int]] = kwargs.get('unidirectional')
        self.multidirectional: Optional[int] = kwargs.get('multidirectional')

@dataclass
class GlossaryTerm:
    language: str
    value: str

@dataclass
class DocumentOptions:
    adapt_to: Optional[List[str]] = None
    glossaries: Optional[List[str]] = None
    no_trace: Optional[bool] = None
    style: Optional[TranslationStyle] = None

# Extraction parameters for DOCX files
@dataclass
class DocxExtractionParams:
    extract_comments: Optional[bool] = None
    accept_revisions: Optional[bool] = None

    def to_dict(self) -> Dict[str, Union[str, bool]]:
        result = {}
        if self.extract_comments is not None:
            result['extract_comments'] = self.extract_comments
        if self.accept_revisions is not None:
            result['accept_revisions'] = self.accept_revisions
        return result

# Union type for all extraction parameter types
DocumentExtractionParams = Union[DocxExtractionParams]

class Document(LaraObject):

    def __init__(self, **kwargs):
        self.id: str = kwargs.get('id')
        self.status: DocumentStatus = DocumentStatus(kwargs.get('status'))
        self.source: Optional[str] = kwargs.get('source')
        self.target: str = kwargs.get('target')
        self.filename: str = kwargs.get('filename')
        self.created_at: datetime = self._parse_date(kwargs.get('created_at'))
        self.updated_at: datetime = self._parse_date(kwargs.get('updated_at'))
        self.options: Optional[DocumentOptions] = DocumentOptions(**kwargs.get('options')) if kwargs.get('options') else None
        self.translated_chars: Optional[int] = int(kwargs.get('translated_chars')) if kwargs.get('translated_chars') else None
        self.total_chars: Optional[int] = int(kwargs.get('total_chars')) if kwargs.get('total_chars') else None
        self.error_reason: Optional[str] = kwargs.get('error_reason')


class TextBlock(LaraObject):
    def __init__(self, **kwargs):
        self.text: str = kwargs.get('text')
        self.translatable: bool = kwargs.get('translatable', True)

class NGMemoryMatch(LaraObject):
    def __init__(self, **kwargs):
        self.memory: str = kwargs.get('memory')
        self.tuid: Optional[str] = kwargs.get('tuid') if kwargs.get('tuid') else None
        self.language: List[str] = kwargs.get('language')
        self.sentence: str = kwargs.get('sentence')
        self.translation: float = kwargs.get('translation')

class NGGlossaryMatch(LaraObject):
    def __init__(self, **kwargs):
        self.glossary: str = kwargs.get('glossary')
        self.language: List[str] = kwargs.get('language')
        self.term: str = kwargs.get('term')
        self.translation: str = kwargs.get('translation')

class TextResult(LaraObject):
    def __init__(self, **kwargs):
        self.content_type: str = kwargs.get('content_type')
        self.source_language: str = kwargs.get('source_language')
        self.translation: Union[str, List[str], List[TextBlock]]
        self.adapted_to: Optional[List[str]] = kwargs.get('adapted_to', None)
        self.glossaries: Optional[List[str]] = kwargs.get('glossaries', None)
        self.adapted_to_matches: Optional[Union[List[NGMemoryMatch], List[Optional[List[NGMemoryMatch]]]]] = None
        self.glossaries_matches: Optional[Union[List[NGGlossaryMatch], List[Optional[List[NGGlossaryMatch]]]]] = None

        # Parse adapted_to_matches
        adapted_to_matches = kwargs.get('adapted_to_matches', None)
        if adapted_to_matches is not None:
            if any(isinstance(m, list) for m in adapted_to_matches):
                self.adapted_to_matches = [
                    [NGMemoryMatch(**m) for m in matches] if isinstance(matches, list) else None
                    for matches in adapted_to_matches
                ]
            else:
                self.adapted_to_matches = [NGMemoryMatch(**m) for m in adapted_to_matches]

        # Parse glossaries_matches
        glossaries_matches = kwargs.get('glossaries_matches', None)
        if glossaries_matches is not None:
            if any(isinstance(m, list) for m in glossaries_matches):
                self.glossaries_matches = [
                    [NGGlossaryMatch(**m) for m in matches] if isinstance(matches, list) else None
                    for matches in glossaries_matches
                ]
            else:
                self.glossaries_matches = [NGGlossaryMatch(**m) for m in glossaries_matches]

        # Parse translation
        translation = kwargs.get('translation')
        if isinstance(translation, str):
            self.translation = translation
        elif isinstance(translation, list):
            if all(isinstance(e, str) for e in translation):
                self.translation = translation
            else:
                self.translation = [TextBlock(**e) for e in translation]


class DetectPrediction(LaraObject):
    def __init__(self, **kwargs):
        self.language: str = kwargs.get('language')
        self.confidence: float = kwargs.get('confidence')

class DetectResult(LaraObject):
    def __init__(self, **kwargs):
        self.language: str = kwargs.get('language')
        self.content_type: str = kwargs.get('content_type')
        self.predictions: List[DetectPrediction] = [DetectPrediction(**p) for p in kwargs.get('predictions', [])]


# Translator SDK -------------------------------------------------------------------------------------------------------


class Memories:
    def __init__(self, client: LaraClient):
        self._client: LaraClient = client
        self._polling_interval: int = 2

    def list(self) -> List[Memory]:
        return [Memory(**e) for e in self._client.get('/v2/memories')]

    def create(self, name: str, external_id: str = None) -> Memory:
        return Memory(**self._client.post('/v2/memories', {
            'name': name, 'external_id': external_id
        }))

    def get(self, id_: str) -> Optional[Memory]:
        try:
            return Memory(**self._client.get(f'/v2/memories/{id_}'))
        except LaraApiError as e:
            if e.status_code == 404:
                return None
            raise

    def delete(self, id_: str) -> Memory:
        return Memory(**self._client.delete(f'/v2/memories/{id_}'))

    def update(self, id_: str, name: str) -> Memory:
        return Memory(**self._client.put(f'/v2/memories/{id_}', {
            'name': name
        }))

    def connect(self, ids: Union[str, List[str]]) -> Union[Optional[Memory], List[Memory]]:
        results = [Memory(**e) for e in self._client.post('/v2/memories/connect', {
            'ids': ids if isinstance(ids, list) else [ids]
        })]

        if isinstance(ids, list):
            return results
        return results[0] if len(results) > 0 else None

    def import_tmx(self, id_: str, tmx: str) -> MemoryImport:
        with open(tmx, 'rb') as stream:
            compressed_stream = GZIPCompressedStream(stream, compression_level=7)
            return MemoryImport(**self._client.post(f'/v2/memories/{id_}/import',
                                                    {'compression': 'gzip'}, {'tmx': compressed_stream}))

    def add_translation(self, id_: Union[str, List[str]], source: str, target: str, sentence: str, translation: str,
                        *, tuid: str = None, sentence_before: str = None, sentence_after: str = None,
                        headers: Optional[Dict[str, str]] = None) -> MemoryImport:
        body = {'source': source, 'target': target, 'sentence': sentence, 'translation': translation,
                'tuid': tuid, 'sentence_before': sentence_before, 'sentence_after': sentence_after}

        if isinstance(id_, list):
            body['ids'] = id_
            return MemoryImport(**self._client.put('/v2/memories/content', body, headers=headers))
        return MemoryImport(**self._client.put(f'/v2/memories/{id_}/content', body, headers=headers))

    def delete_translation(self, id_: Union[str, List[str]], source: str, target: str,
                           *, sentence: Optional[str] = None, translation: Optional[str] = None,
                           tuid: Optional[str] = None, sentence_before: Optional[str] = None,
                           sentence_after: Optional[str] = None
                           ) -> MemoryImport:
        body = {'source': source, 'target': target, 'sentence': sentence, 'translation': translation,
                'tuid': tuid, 'sentence_before': sentence_before, 'sentence_after': sentence_after}

        if isinstance(id_, list):
            body['ids'] = id_
            return MemoryImport(**self._client.delete('/v2/memories/content', body))
        return MemoryImport(**self._client.delete(f'/v2/memories/{id_}/content', body))

    def get_import_status(self, id_: str) -> MemoryImport:
        return MemoryImport(**self._client.get(f'/v2/memories/imports/{id_}'))

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

class Glossaries:
    def __init__(self, client: LaraClient):
        self._client: LaraClient = client
        self._polling_interval: int = 2

    def list(self) -> List[Glossary]:
        return [Glossary(**e) for e in self._client.get('/v2/glossaries')]

    def create(self, name: str) -> Glossary:
        return Glossary(**self._client.post('/v2/glossaries', {
            'name': name
        }))

    def get(self, id_: str) -> Optional[Glossary]:
        try:
            return Glossary(**self._client.get(f'/v2/glossaries/{id_}'))
        except LaraApiError as e:
            if e.status_code == 404:
                return None
            raise

    def delete(self, id_: str) -> Glossary:
        return Glossary(**self._client.delete(f'/v2/glossaries/{id_}'))

    def update(self, id_: str, name: str) -> Glossary:
        return Glossary(**self._client.put(f'/v2/glossaries/{id_}', {
            'name': name
        }))

    def import_csv(self, id_: str, csv: str, content_type: GlossaryFileFormat = "csv/table-uni") -> GlossaryImport:
        with open(csv, 'rb') as stream:
            compressed_stream = GZIPCompressedStream(stream, compression_level=7)
            return GlossaryImport(**self._client.post(f'/v2/glossaries/{id_}/import',
                                                    {'compression': 'gzip', 'content_type': content_type},
                                                    {'csv': compressed_stream}))

    def get_import_status(self, id_: str) -> GlossaryImport:
        return GlossaryImport(**self._client.get(f'/v2/glossaries/imports/{id_}'))

    def wait_for_import(self, glossary_import: GlossaryImport, *,
                        update_callback: Callable[[GlossaryImport], None] = None,
                        max_wait_time: float = 0) -> GlossaryImport:
        start = time.time()
        while glossary_import.progress < 1.:
            if 0 < max_wait_time < time.time() - start:
                raise TimeoutError()

            time.sleep(self._polling_interval)

            glossary_import = self.get_import_status(glossary_import.id)
            if update_callback is not None:
                update_callback(glossary_import)

        return glossary_import

    def counts(self, id_: str) -> GlossaryCounts:
        return GlossaryCounts(**self._client.get(f'/v2/glossaries/{id_}/counts'))


    def export(self, id_: str, content_type: GlossaryFileFormat, source: Optional[str] = None) -> bytes:
        response = self._client.get(f'/v2/glossaries/{id_}/export', {
            'content_type': content_type,
            'source': source
        })
        return response

    def add_or_replace_entry(self, id_: str, terms: List[GlossaryTerm], *, guid: Optional[str] = None) -> GlossaryImport:
        body = {'terms': [term.__dict__ for term in terms], 'guid': guid}
        return GlossaryImport(**self._client.put(f'/v2/glossaries/{id_}/content', body))

    def delete_entry(self, id_: str, *, term: Optional[GlossaryTerm] = None, guid: Optional[str] = None) -> GlossaryImport:
        body = {'term': term.__dict__ if term else None, 'guid': guid}
        return GlossaryImport(**self._client.delete(f'/v2/glossaries/{id_}/content', body))



class DocumentStatus(Enum):
    INITIALIZED = 'initialized'     # just been created
    ANALYZING = 'analyzing'         # being analyzed for language detection and chars count
    PAUSED = 'paused'               # paused after analysis, needs user confirm
    READY = 'ready'                 # ready to be translated
    TRANSLATING = 'translating'
    TRANSLATED = 'translated'
    ERROR = 'error'


class AudioStatus(Enum):
    INITIALIZED = 'initialized'
    ANALYZING = 'analyzing'
    PAUSED = 'paused'
    READY = 'ready'
    TRANSLATING = 'translating'
    TRANSLATED = 'translated'
    ERROR = 'error'


class VoiceGender(Enum):
    MALE = 'male'
    FEMALE = 'female'


@dataclass
class AudioOptions:
    adapt_to: Optional[List[str]] = None
    glossaries: Optional[List[str]] = None
    no_trace: Optional[bool] = None
    style: Optional[TranslationStyle] = None
    voice_gender: Optional[VoiceGender] = None


class Audio(LaraObject):

    def __init__(self, **kwargs):
        self.id: str = kwargs.get('id')
        self.status: AudioStatus = AudioStatus(kwargs.get('status'))
        self.source: Optional[str] = kwargs.get('source')
        self.target: str = kwargs.get('target')
        self.filename: str = kwargs.get('filename')
        self.created_at: datetime = self._parse_date(kwargs.get('created_at'))
        self.updated_at: datetime = self._parse_date(kwargs.get('updated_at'))
        self.options: Optional[AudioOptions] = AudioOptions(**kwargs.get('options')) if kwargs.get('options') else None
        self.translated_seconds: Optional[int] = int(kwargs.get('translated_seconds')) if kwargs.get('translated_seconds') else None
        self.total_seconds: Optional[int] = int(kwargs.get('total_seconds')) if kwargs.get('total_seconds') else None
        self.error_reason: Optional[str] = kwargs.get('error_reason')


class Documents:
    def __init__(self, client: LaraClient):
        self._client: LaraClient = client
        self._s3client = S3Client()
        self._polling_interval: int = 2

    def upload(self, file_path: str, filename: str, target: str, source: Optional[str] = None,
               adapt_to: Optional[List[str]] = None, glossaries: Optional[List[str]] = None, no_trace: bool = False,
               style: Optional[TranslationStyle] = None, password: Optional[str] = None,
               extraction_params: Optional[DocumentExtractionParams] = None) -> Document:
        with open(file_path, 'rb') as file_payload:
            response_data = self._client.get('/v2/documents/upload-url', {'filename': filename})

            url: str = response_data['url']
            fields: S3UploadFields = S3UploadFields(**response_data['fields'])

            self._s3client.upload(url, fields, file_payload)

        body = {
            's3key': fields['key'],
            'target': target,
        }
        if source is not None:
            body['source'] = source

        if adapt_to is not None:
            body['adapt_to'] = adapt_to

        if glossaries is not None:
            body['glossaries'] = glossaries

        if password is not None:
            body['password'] = password

        if style is not None:
            body['style'] = style

        if extraction_params is not None:
            body['extraction_params'] = extraction_params.to_dict()

        headers = None
        if no_trace is True:
            headers = {'X-No-Trace': 'true'}

        return Document(**self._client.post('/v2/documents', body, headers=headers))

    def status(self, id: str) -> Document:
        return Document(**self._client.get(f'/v2/documents/{id}'))

    def download(self, id: str, output_format: Optional[str] = None) -> bytes:
        params = {}
        if output_format is not None:
            params['output_format'] = output_format
        url: str = self._client.get(f'/v2/documents/{id}/download-url', params)['url']
        return self._s3client.download(url=url)

    def translate(self, file_path: str, filename: str, target: str, source: Optional[str] = None,
                  adapt_to: Optional[List[str]] = None, glossaries: Optional[List[str]] = None, output_format: Optional[str] = None,
                  no_trace: bool = False, style: Optional[TranslationStyle] = None, password: Optional[str] = None,
                  extraction_params: Optional[DocumentExtractionParams] = None) -> bytes:

        document = self.upload(file_path=file_path, filename=filename, target=target, source=source, adapt_to=adapt_to,
                               glossaries=glossaries, no_trace=no_trace, style=style, password=password, extraction_params=extraction_params)

        max_wait_time = 60 * 15 # 15 minutes
        start = time.time()

        while time.time() - start < max_wait_time:
            document = self.status(id=document.id)

            if document.status == DocumentStatus.TRANSLATED:
                return self.download(id=document.id, output_format=output_format)
            elif document.status == DocumentStatus.ERROR:
                raise LaraApiError(500, "DocumentError", document.error_reason)

            time.sleep(self._polling_interval)
        raise TimeoutError()

class AudioTranslator:
    def __init__(self, client: LaraClient):
        self._client: LaraClient = client
        self._s3client = S3Client()
        self._polling_interval: int = 2

    def upload(self, file_path: str, filename: str, target: str, source: Optional[str] = None,
               adapt_to: Optional[List[str]] = None, glossaries: Optional[List[str]] = None,
               no_trace: bool = False, style: Optional[TranslationStyle] = None,
               voice_gender: Optional[VoiceGender] = None) -> Audio:
        with open(file_path, 'rb') as file_payload:
            response_data = self._client.get('/v2/audio/upload-url', {'filename': filename})

            url: str = response_data['url']
            fields: S3UploadFields = S3UploadFields(**response_data['fields'])

            self._s3client.upload(url, fields, file_payload)

        body = {
            's3key': fields['key'],
            'target': target,
        }
        if source is not None:
            body['source'] = source

        if adapt_to is not None:
            body['adapt_to'] = adapt_to

        if glossaries is not None:
            body['glossaries'] = glossaries

        if style is not None:
            body['style'] = style
        if voice_gender is not None:
            body['voice_gender'] = voice_gender.value

        headers = None
        if no_trace is True:
            headers = {'X-No-Trace': 'true'}

        return Audio(**self._client.post('/v2/audio/translate', body, headers=headers))

    def status(self, id: str) -> Audio:
        return Audio(**self._client.get(f'/v2/audio/{id}'))

    def download(self, id: str) -> bytes:
        url: str = self._client.get(f'/v2/audio/{id}/download-url')['url']
        return self._s3client.download(url=url)

    def translate(self, file_path: str, filename: str, target: str, source: Optional[str] = None,
                  adapt_to: Optional[List[str]] = None, glossaries: Optional[List[str]] = None,
                  no_trace: bool = False, style: Optional[TranslationStyle] = None,
                  voice_gender: Optional[VoiceGender] = None) -> bytes:

        audio = self.upload(file_path=file_path, filename=filename, target=target, source=source,
                            adapt_to=adapt_to, glossaries=glossaries, no_trace=no_trace, style=style,
                            voice_gender=voice_gender)

        max_wait_time = 60 * 15 # 15 minutes
        start = time.time()

        while time.time() - start < max_wait_time:
            audio = self.status(id=audio.id)

            if audio.status == AudioStatus.TRANSLATED:
                return self.download(id=audio.id)
            elif audio.status == AudioStatus.ERROR:
                raise LaraApiError(500, "AudioError", audio.error_reason)

            time.sleep(self._polling_interval)
        raise TimeoutError()

class ImageParagraph(LaraObject):
    def __init__(self, **kwargs):
        self.text: str = kwargs.get('text')
        self.translation: str = kwargs.get('translation')
        self.adapted_to_matches: Optional[List[NGMemoryMatch]] = [NGMemoryMatch(**m) for m in kwargs.get('adapted_to_matches', [])] if kwargs.get('adapted_to_matches') is not None else None
        self.glossaries_matches: Optional[List[NGGlossaryMatch]] = [NGGlossaryMatch(**m) for m in kwargs.get('glossaries_matches', [])] if kwargs.get('glossaries_matches') is not None else None

class ImageTextResult(LaraObject):
    def __init__(self, **kwargs):
        self.source_language: str = kwargs.get('source_language')
        self.adapted_to: Optional[List[str]] = kwargs.get('adapted_to', None)
        self.glossaries: Optional[List[str]] = kwargs.get('glossaries', None)
        self.paragraphs: List[ImageParagraph] = [ImageParagraph(**p) for p in kwargs.get('paragraphs', [])]

class ImageTranslator:
    def __init__(self, client: LaraClient):
        self._client: LaraClient = client

    def translate(self, image_path: str, target: str, source: Optional[str] = None, *,
                  adapt_to: Optional[List[str]] = None, glossaries: Optional[List[str]] = None,
                  no_trace: bool = False, style: Optional[TranslationStyle] = None,
                  text_removal: Optional[Literal["overlay", "inpainting"]] = None) -> bytes:
        with open(image_path, 'rb') as file_payload:
            mime_type, _ = mimetypes.guess_type(image_path)
            if mime_type is None:
                raise ValueError(f'Could not determine MIME type for file: {image_path}')
            image_data = file_payload
            filename = Path(image_path).name

            data = {
                'target': target,
            }
            if source is not None:
                data['source'] = source
            if adapt_to is not None:
                data['adapt_to'] = json.dumps(adapt_to)
            if glossaries is not None:
                data['glossaries'] = json.dumps(glossaries)
            if style is not None:
                data['style'] = style
            if text_removal is not None:
                data['text_removal'] = text_removal

            headers = {}
            if no_trace is True:
                headers['X-No-Trace'] = 'true'
            files = {'image': (filename, image_data, mime_type)}

            return self._client.post('/v2/images/translate', body=data, files=files, headers=headers)

    def translate_text(self, image_path: str, target: str, source: Optional[str] = None, *,
                  adapt_to: Optional[List[str]] = None, glossaries: Optional[List[str]] = None,
                  no_trace: bool = False, style: Optional[TranslationStyle] = None, verbose: Optional[bool] = False) -> ImageTextResult:

        with open(image_path, 'rb') as file_payload:
            mime_type, _ = mimetypes.guess_type(image_path)
            if mime_type is None:
                raise ValueError(f'Could not determine MIME type for file: {image_path}')
            image_data = file_payload
            filename = Path(image_path).name

            data = {
                'target': target,
            }
            if source is not None:
                data['source'] = source
            if adapt_to is not None:
                data['adapt_to'] = json.dumps(adapt_to)
            if glossaries is not None:
                data['glossaries'] = json.dumps(glossaries)
            if style is not None:
                data['style'] = style
            if verbose:
                data['verbose'] = json.dumps(verbose)

            headers = {}
            if no_trace is True:
                headers['X-No-Trace'] = 'true'
            files = {'image': (filename, image_data, mime_type)}
            return ImageTextResult(**self._client.post('/v2/images/translate-text', body=data, files=files, headers=headers))


class TranslatePriority(Enum):
    NORMAL = 'normal'
    BACKGROUND = 'background'


class UseCache(Enum):
    YES = 'yes'
    NO = 'no'
    OVERWRITE = 'overwrite'


class Translator:
    def __init__(self, credentials: Union[AccessKey, AuthToken, Credentials] = None, *,
                 access_key_id: str = None, access_key_secret: str = None, server_url: str = None):
        """
        Initialize the Translator with authentication.

        :param auth: Authentication object (AccessKey, AuthToken, or deprecated Credentials)
        :param access_key_id: (Deprecated) Use AccessKey(id, secret) instead
        :param access_key_secret: (Deprecated) Use AccessKey(id, secret) instead
        :param server_url: Optional custom server URL
        """
        if credentials is None:
            if access_key_id is not None and access_key_secret is not None:
                # Legacy support for old-style initialization
                import warnings
                warnings.warn(
                    "Passing access_key_id and access_key_secret as keyword arguments is deprecated. "
                    "Use AccessKey(id, secret) instead.",
                    DeprecationWarning,
                    stacklevel=2
                )
                credentials = AccessKey(access_key_id, access_key_secret)
            else:
                raise ValueError('auth parameter is required (AccessKey, AuthToken, or Credentials)')

        self._client: LaraClient = LaraClient(credentials, server_url)
        self.memories: Memories = Memories(self._client)
        self.documents: Documents = Documents(self._client)
        self.glossaries: Glossaries = Glossaries(self._client)
        self.audio: AudioTranslator = AudioTranslator(self._client)
        self.images: ImageTranslator = ImageTranslator(self._client)

    def languages(self) -> List[str]:
        return self._client.get('/v2/languages')

    def translate(self, text: Union[str, Iterable[str], Iterable[TextBlock]], *,
                  source: str = None, source_hint: str = None, target: str, adapt_to: List[str] = None,
                  glossaries: List[str] = None, instructions: List[str] = None, content_type: str = None,
                  multiline: bool = True, timeout_ms: int = None, priority: TranslatePriority = None,
                  use_cache: Union[bool, UseCache] = None, cache_ttl_s: int = None,
                  no_trace: bool = False, verbose: bool = False, style: Optional[TranslationStyle] = None,
                  headers: Optional[Dict[str, str]] = None, reasoning: bool = False,
                  callback: Optional[Callable[[TextResult], None]] = None) -> TextResult:
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

        body = {
            'source': source, 'target': target, 'source_hint': source_hint, 'content_type': content_type,
            'multiline': multiline, 'adapt_to': adapt_to, 'instructions': instructions, 'timeout': timeout_ms, 'q': q,
            'priority': priority.value if priority is not None else None,
            'use_cache': use_cache.value if use_cache is not None else None, 'cache_ttl': cache_ttl_s,
            'glossaries': glossaries, 'verbose': verbose, 'style': style, 'reasoning': reasoning
        }

        request_headers = {}
        if headers is not None:
            request_headers.update(headers)
        if no_trace is True:
            request_headers['X-No-Trace'] = 'true'

        last_result = None
        for partial in self._client.post_and_get_stream('/translate', body, headers=request_headers):
            last_result = partial
            if callback is not None and reasoning:
                callback(TextResult(**partial))

        if last_result is None:
            raise ValueError('No translation result received.')

        return TextResult(**last_result)

    def detect(self, text: Union[str, List[str]], *, hint: Optional[str] = None,
               passlist: Optional[List[str]] = None) -> DetectResult:
        body = {
            'q': text,
            'hint': hint,
            'passlist': passlist
        }

        return DetectResult(**self._client.post('/v2/detect', body))