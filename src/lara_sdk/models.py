from datetime import datetime
from typing import Optional, Dict, Union, List, Any


class Model(object):
    @staticmethod
    def _parse_date(date: Optional[str]) -> Optional[datetime]:
        if date is None:
            return None
        if date.endswith("Z"):
            date = date[:-1] + "+00:00"
        return datetime.fromisoformat(date) if date is not None else None

    def __init__(self, data: Dict):
        self.id: str = data.get("id")
        self.created_at: datetime = self._parse_date(data.get("created_at", None))
        self.updated_at: datetime = self._parse_date(data.get("updated_at", None))

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        result = f"{self.__class__.__name__}("
        for name, value in self.__dict__.items():
            if isinstance(value, datetime):
                value = value.isoformat()
            if isinstance(value, str):
                value = f'"{value}"'
            result += f"{name}={value}, "

        return result[:-2] + ")"


class Memory(Model):
    @classmethod
    def parse(cls, data: Optional[Dict]) -> Optional[Union['Memory', List['Memory']]]:
        if data is None:
            return None

        return [cls(item) for item in data] if isinstance(data, list) else cls(data)

    def __init__(self, data: Dict):
        super().__init__(data)
        self.name: str = data.get("name")
        self.external_id: Optional[str] = data.get("external_id", None)
        self.secret: Optional[str] = data.get("secret", None)
        self.owner_id: str = data.get("owner_id")
        self.collaborators_count: int = data.get("collaborators_count")
        self.shared_at: datetime = self._parse_date(data.get("shared_at"))


class MemoryImport(Model):
    @classmethod
    def parse(cls, data: Optional[Dict]) -> Optional[Union['MemoryImport', List['MemoryImport']]]:
        if data is None:
            return None

        return [cls(item) for item in data] if isinstance(data, list) else cls(data)

    def __init__(self, data: Dict):
        super().__init__(data)
        self.id: str = data.get("id")
        self.begin: int = data.get("begin")
        self.end: int = data.get("end")
        self.channel: int = data.get("channel")
        self.size: int = data.get("size")
        self.progress: float = data.get("progress")


class Document(object):
    @classmethod
    def wrap(cls, text: Union[str, List[str]]) -> 'Document':
        document = Document()
        if isinstance(text, str):
            document.add_section(text)
        else:
            for item in text:
                document.add_section(item)
        return document

    @staticmethod
    def is_acceptable_metadata_value(value: Any) -> bool:
        if value is None:
            return True

        if isinstance(value, str) or isinstance(value, int) or isinstance(value, float) or isinstance(value, bool):
            return True

        if isinstance(value, dict):
            for v in value.values():
                if not Document.is_acceptable_metadata_value(v):
                    return False
            return True

        if isinstance(value, list):
            for v in value:
                if not Document.is_acceptable_metadata_value(v):
                    return False
            return True

        return False

    @classmethod
    def parse(cls, source: 'Document', data: Optional[Dict]) -> Optional['Document']:
        if data is None:
            return None

        document = Document(content_type=data.get("content_type", None))
        document._detected_language = data.get("detected_language", None)
        document._adapted_to = data.get("adapted_to", None)

        for source_section, translation in zip(source.sections, data.get("translations", [])):
            document.add_section(translation.get("text") if translation is not None else source_section.text,
                                 source_section.translatable,
                                 source_section.metadata)
        return document

    class Section(object):
        def __init__(self, text: str, translatable: bool = True, metadata: Dict = None):
            self.text: str = text
            self.translatable: bool = translatable
            self.metadata: Optional[Dict] = metadata

            if metadata is not None:
                for value in metadata.values():
                    if not Document.is_acceptable_metadata_value(value):
                        raise ValueError("Metadata values must be strings, numbers, booleans, lists or dictionaries")

        def __repr__(self):
            return self.__str__()

        def __str__(self):
            return f"Section(text=\"{self.text}\", translatable={self.translatable}, metadata={self.metadata})"

    def __init__(self, content_type: str = None):
        self.content_type: Optional[str] = content_type
        self.sections: List['Document.Section'] = []

        self._detected_language: Optional[str] = None
        self._adapted_to: Optional[List[str]] = None

    @property
    def detected_language(self) -> Optional[str]:
        return self._detected_language

    @property
    def adapted_to(self) -> Optional[List[str]]:
        return self._adapted_to

    def add_section(self, text: str, translatable: bool = True, metadata: Dict = None):
        self.sections.append(Document.Section(text, translatable, metadata))

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return str(self.sections)
