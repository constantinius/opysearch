from dataclasses import dataclass, field
from datetime import datetime
from typing import Iterator, List, Optional, Tuple, Union

from opynsearch.description import Option


@dataclass
class SearchResult:
    total_results: int
    start_index: int
    items_per_page: int

    pages: Iterator["SearchResultPage"]

    @property
    def items(self) -> Iterator["SearchResultItem"]:
        for page in self.pages:
            yield from page.items


@dataclass
class SearchResultPage:
    title: str
    id: str
    source: str
    total_results: int
    start_index: int
    items_per_page: int
    items: List["SearchResultItem"]

    creator: Optional[str] = None
    subjects: List[str] = field(default_factory=list)
    abstract: Optional[str] = None
    publisher: Optional[str] = None
    contributors: List[str] = field(default_factory=list)
    modified: Optional[Union[datetime, Tuple[datetime, datetime]]] = None
    identifier: Optional[str] = None
    language: Optional[str] = None
    rights: Optional[str] = None
    envelopes: List[str] = field(default_factory=list)

    next_page: Optional[str] = None
    previous_page: Optional[str] = None
    first_page: Optional[str] = None
    last_page: Optional[str] = None


@dataclass
class SearchResultItem:
    title: str
    id: str
    identifier: str
    creator: Optional[str] = None
    subjects: List[str] = field(default_factory=list)
    abstract: Optional[str] = None
    contributors: List[str] = field(default_factory=list)
    modified: Optional[Union[datetime, Tuple[datetime, datetime]]] = None
    date: Optional[Union[datetime, Tuple[datetime, datetime]]] = None
    sources: List[str] = field(default_factory=list)
    language: Optional[str] = None
    rights: Optional[str] = None
    envelope: Optional[str] = None
    # relation:
