from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Union


@dataclass
class Option:
    value: str
    label: Optional[str] = None


LimitType = Union[int, float, str]  # TODO: datetime?
StepType = Union[int, float, str]  # TODO timedelta?


@dataclass
class Parameter:
    name: str
    value: Optional[str] = None
    minimum: int = 1
    maximum: int = 1
    pattern: Optional[str] = None
    title: Optional[str] = None
    min_exclusive: Optional[LimitType] = None
    max_exclusive: Optional[LimitType] = None
    min_inclusive: Optional[LimitType] = None
    max_inclusive: Optional[LimitType] = None
    step: Optional[StepType] = None
    options: List[Option] = field(default_factory=list)


class HttpMethod(Enum):
    OPTIONS = "OPTIONS"
    GET = "GET"
    HEAD = "HEAD"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    TRACE = "TRACE"
    CONNECT = "CONNECT"


@dataclass
class Url:
    template: str
    type: str
    rel: Optional[str] = "results"
    index_offset: int = 1
    page_offset: int = 1
    method: HttpMethod = HttpMethod.GET
    enctype: Optional[str] = None
    parameters: List[Parameter] = field(default_factory=list)


@dataclass
class Image:
    url: str
    width: Optional[int] = None
    height: Optional[int] = None
    type: Optional[str] = None


ExtraParameterName = Tuple[str, str]


@dataclass
class Query:
    role: str
    title: Optional[str] = None
    total_results: Optional[int] = None
    search_terms: Optional[str] = None
    count: Optional[int] = None
    start_index: Optional[int] = None
    start_page: Optional[int] = None
    language: Optional[str] = None
    input_encoding: Optional[str] = None
    output_encoding: Optional[str] = None
    extra_parameters: Dict[ExtraParameterName, str] = field(default_factory=dict)


class SyndicationRight(Enum):
    open = "open"
    limited = "limited"
    private = "private"
    closed = "closed"


@dataclass
class Description:
    short_name: str
    description: str
    urls: List[Url]
    tags: List[str] = field(default_factory=list)
    images: List[Image] = field(default_factory=list)
    long_name: Optional[str] = None
    contact: Optional[str] = None
    queries: List[Query] = field(default_factory=list)
    developer: Optional[str] = None
    attribution: Optional[str] = None
    syndication_right: SyndicationRight = SyndicationRight.open
    adult_content: bool = False
    languages: List[str] = field(default_factory=lambda: ["*"])
    input_encodings: List[str] = field(default_factory=lambda: ["UTF-8"])
    output_encodings: List[str] = field(default_factory=lambda: ["UTF-8"])
