from typing import cast, Callable, List, Optional, TypeVar, Union, BinaryIO
from lxml.etree import QName, parse as parse_xml, _Element as Element, _ElementTree as ElementTree
from io import BytesIO

from .description import (
    Description, LimitType, StepType, SyndicationRight, Url, Image, Query, Parameter, Option
)

NS_OSDD = "http://a9.com/-/spec/opensearch/1.1/"
NS_PARAM = "http://a9.com/-/spec/opensearch/extensions/parameters/1.0/"
NAMESPACES = {
    "os": NS_OSDD,
    "param": NS_PARAM,
}


T = TypeVar("T", int, float, str, SyndicationRight, List[str])


def unwrap(raw: Optional[str], parser: Callable[[str], T], default: T = None) -> Optional[T]:
    if raw is not None:
        return parser(raw)
    return default


def unwrap_default(raw: Optional[str], parser: Callable[[str], T], default: T) -> T:
    if raw is not None:
        return parser(raw)
    return default


def parse_limit(value: str) -> LimitType:
    try:
        return int(value)
    except ValueError:
        pass
    try:
        return float(value)
    except ValueError:
        pass
    return value


def parse_step(value: str) -> StepType:
    try:
        return int(value)
    except ValueError:
        pass
    try:
        return float(value)
    except ValueError:
        pass
    return value


def parse_osdd11(source: Union[BinaryIO, bytes]) -> Description:
    if isinstance(source, bytes):
        source = BytesIO(source)
    tree: Union[Element, ElementTree] = parse_xml(source)
    root = tree if isinstance(tree, Element) else tree.getroot()

    if QName(root) != QName(NS_OSDD, "OpenSearchDescription"):
        raise ValueError(f"Node {root} is not a valid OpenSearch 1.1 description")

    return Description(
        short_name=root.findtext("os:ShortName", namespaces=NAMESPACES),
        description=root.findtext("os:Description", namespaces=NAMESPACES),
        urls=[
            Url(
                template=url.attrib["template"],
                type=url.attrib["type"],
                rel=url.attrib.get("rel", "results"),
                index_offset=int(url.attrib.get("indexOffset", 1)),
                page_offset=int(url.attrib.get("pageOffset", 1)),
                method=HttpMethod(url.get("method", "GET").upper()),
                enctype=url.get("enctype"),
                parameters=[
                    Parameter(
                        name=param.attrib["name"],
                        value=param.attrib.get("value"),
                        minimum=int(param.attrib.get("minimum", 1)),
                        maximum=int(param.attrib.get("maximum", 1)),
                        pattern=param.attrib.get("pattern"),
                        title=param.attrib.get("title"),
                        min_exclusive=cast(
                            LimitType,
                            unwrap(
                                param.attrib.get("minExclusive"),
                                parse_limit,
                            ),
                        ),
                        max_exclusive=cast(
                            LimitType,
                            unwrap(
                                param.attrib.get("maxExclusive"),
                                parse_limit,
                            ),
                        ),
                        min_inclusive=cast(
                            LimitType,
                            unwrap(
                                param.attrib.get("minInclusive"),
                                parse_limit,
                            ),
                        ),
                        max_inclusive=cast(
                            LimitType,
                            unwrap(
                                param.attrib.get("maxInclusive"),
                                parse_limit,
                            ),
                        ),
                        step=cast(
                            StepType,
                            unwrap(
                                param.attrib.get("step"),
                                parse_limit,
                            ),
                        ),
                        options=[
                            Option(option.attrib["value"], option.attrib.get("label"))
                            for option in url.findall("param:Option", NAMESPACES)
                        ]
                    )
                    for param in url.findall("param:Parameter", NAMESPACES)
                ]
            )
            for url in root.findall("os:Url", NAMESPACES)
        ],
        tags=unwrap_default(
            root.findtext("os:Tags", namespaces=NAMESPACES),
            lambda v: v.split(),
            []
        ),
        images=[
            Image(
                url=image.text,
                width=unwrap(image.attrib.get("width"), int),
                height=unwrap(image.attrib.get("height"), int),
                type=image.attrib.get("type"),
            )
            for image in root.findall("os:Image", NAMESPACES)
        ],
        long_name=root.findtext("os:LongName", namespaces=NAMESPACES),
        contact=root.findtext("os:Contact", namespaces=NAMESPACES),
        queries=[
            Query(
                role=query.attrib["role"],
                title=query.attrib.get("title"),
                total_results=unwrap(query.attrib.get("totalResults"), int),
                search_terms=query.attrib.get("searchTerms"),
                count=unwrap(query.attrib.get("count"), int),
                start_index=unwrap(query.attrib.get("startIndex"), int),
                start_page=unwrap(query.attrib.get("startPage"), int),
                language=query.attrib.get("language"),
                input_encoding=query.attrib.get("inputEncoding"),
                output_encoding=query.attrib.get("outputEncoding"),
                extra_parameters={
                    (QName(key).namespace, QName(key).localname): value
                    for key, value in query.attrib.items()
                    if QName(key).namespace is not None
                }
            )
            for query in root.findall("os:Query", NAMESPACES)
        ],
        developer=root.findtext("os:Developer", namespaces=NAMESPACES),
        attribution=root.findtext("os:Attribution", namespaces=NAMESPACES),
        syndication_right=unwrap_default(
            root.findtext("os:SyndicationRight", namespaces=NAMESPACES),
            SyndicationRight,
            SyndicationRight.open,
        ),
        adult_content=cast(
            bool,
            unwrap_default(
                root.findtext("os:AdultContent", namespaces=NAMESPACES),
                lambda v: v.upper() not in ("false", "FALSE", "0", "no", "NO"),
                False
            )
        ),
        languages=[
            lang.text
            for lang in root.findall("os:Language", namespaces=NAMESPACES)
        ] or ["*"],
        input_encodings=[
            enc.text
            for enc in root.findall("os:InputEncoding", namespaces=NAMESPACES)
        ] or ["UTF-8"],
        output_encodings=[
            enc.text
            for enc in root.findall("os:OutputEncoding", namespaces=NAMESPACES)
        ] or ["UTF-8"],
    )
