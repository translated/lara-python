from datetime import datetime
from typing import Optional, Dict, Union, List, Iterable


class Model(object):
    @staticmethod
    def _parse_date(date: Optional[str]) -> Optional[datetime]:
        if date is None:
            return None
        if date.endswith("Z"):
            date = date[:-1] + "+00:00"
        return datetime.fromisoformat(date) if date is not None else None

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
    def parse(cls, data: Optional[Union[List[Dict], Dict]]) -> Optional[Union['Memory', List['Memory']]]:
        if data is None:
            return None

        return [cls(item) for item in data] if isinstance(data, list) else cls(data)

    def __init__(self, data: Dict):
        self.id: str = data.get("id")
        self.created_at: datetime = self._parse_date(data.get("created_at", None))
        self.updated_at: datetime = self._parse_date(data.get("updated_at", None))
        self.name: str = data.get("name")
        self.external_id: Optional[str] = data.get("external_id", None)
        self.secret: Optional[str] = data.get("secret", None)
        self.owner_id: str = data.get("owner_id")
        self.collaborators_count: int = data.get("collaborators_count")
        self.shared_at: datetime = self._parse_date(data.get("shared_at"))


class MemoryImport(Model):
    @classmethod
    def parse(cls, data: Optional[Union[List[Dict], Dict]]) -> Optional[Union['MemoryImport', List['MemoryImport']]]:
        if data is None:
            return None

        return [cls(item) for item in data] if isinstance(data, list) else cls(data)

    def __init__(self, data: Dict):
        self.id: str = data.get("id")
        self.created_at: datetime = self._parse_date(data.get("created_at", None))
        self.updated_at: datetime = self._parse_date(data.get("updated_at", None))
        self.id: str = data.get("id")
        self.begin: int = data.get("begin")
        self.end: int = data.get("end")
        self.channel: int = data.get("channel")
        self.size: int = data.get("size")
        self.progress: float = data.get("progress")


class Document(object):
    class Section(object):
        def __init__(self, text: str, translatable: bool = True):
            self.text: str = text
            self.translatable: bool = translatable

        def __repr__(self):
            return self.__str__()

        def __str__(self):
            return f"Section(translatable={self.translatable}, \"{self.text}\")"

    def __init__(self, text: Union[str, Iterable[str]] = None):
        self._sections: List['Document.Section'] = []

        if text is not None:
            if isinstance(text, str):
                self.add_section(text)
            else:
                for item in text:
                    self.add_section(item)

    def __iter__(self):
        return iter(self._sections)

    def add_section(self, text: str, translatable: bool = True):
        self._sections.append(self.Section(text, translatable))

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return str(self._sections)


class TextResult(Model):
    @classmethod
    def parse(cls, data: Optional[Union[List[Dict], Dict]]) -> Optional[Union['TextResult', List['TextResult']]]:
        if data is None:
            return None

        return [cls(item) for item in data] if isinstance(data, list) else cls(data)

    def __init__(self, data: Dict):
        self.content_type: str = data.get("content_type")
        self.source_language: str = data.get("source_language")
        self.translation: str = data.get("translation")
        self.adapted_to: Optional[List[str]] = data.get("adapted_to", None)


class DocumentResult(Model):
    def __init__(self, document: Document, data: Dict):
        self.content_type: str = data.get("content_type")
        self.source_language: str = data.get("source_language")
        self.translation: List[Document.Section] = [
            Document.Section(translation or section.text, section.translatable)
            for section, translation in zip(document, data.get("translations"))
        ]
        self.adapted_to: Optional[List[str]] = data.get("adapted_to", None)
