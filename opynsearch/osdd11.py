from datetime import datetime, timedelta
from io import BytesIO
from typing import Any, cast, Callable, List, Optional, TypeVar, Union, BinaryIO

from lxml.etree import QName

from .description import (
    Description, LimitType, StepType, SyndicationRight, Url, Image, Query, Parameter, Option,
    HttpMethod
)
from .utils import unwrap, unwrap_default
from .xml import ElementMaker, Element, parse_xml


NS_OSDD = "http://a9.com/-/spec/opensearch/1.1/"
NS_PARAM = "http://a9.com/-/spec/opensearch/extensions/parameters/1.0/"
NAMESPACES = {
    "os": NS_OSDD,
    "param": NS_PARAM,
}
TYPEMAP = {
    int: lambda _, v: str(v),
    float: lambda _, v: str(v),
    datetime: lambda _, v: datetime.isoformat(v),
    timedelta: lambda _, td: f"PT{td.total_seconds()}S"
}

OS = ElementMaker(
    typemap=TYPEMAP,
    namespace=NS_OSDD,
    nsmap={None: NS_OSDD, "parameter": NS_PARAM}
)
PARAM = ElementMaker(
    typemap=TYPEMAP,
    namespace=NS_PARAM,
    nsmap={None: NS_OSDD, "parameter": NS_PARAM}
)


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
    root = parse_xml(source, (NS_OSDD, "OpenSearchDescription"))
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
                        min_exclusive=unwrap(
                            param.attrib.get("minExclusive"),
                            parse_limit,
                        ),
                        max_exclusive=unwrap(
                            param.attrib.get("maxExclusive"),
                            parse_limit,
                        ),
                        min_inclusive=unwrap(
                            param.attrib.get("minInclusive"),
                            parse_limit,
                        ),
                        max_inclusive=unwrap(
                            param.attrib.get("maxInclusive"),
                            parse_limit,
                        ),
                        step=unwrap(
                            param.attrib.get("step"),
                            parse_limit,
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
        adult_content=unwrap_default(
            root.findtext("os:AdultContent", namespaces=NAMESPACES),
            lambda v: v.upper() not in ("false", "FALSE", "0", "no", "NO"),
            False
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


def encode_osdd11(description: Description, **encode_kwargs: Any) -> Element:
    return OS(
        "OpenSearchDescription",
        OS("ShortName", description.short_name),
        OS("Description", description.description),
        *([
            OS(
                "Url", *[
                    PARAM(
                        "Parameter",
                        name=parameter.name,
                        value=parameter.value,
                        minimum=parameter.minimum,
                        maximum=parameter.maximum,
                        pattern=parameter.pattern,
                        title=parameter.title,
                        minExclusive=parameter.min_exclusive,
                        maxExclusive=parameter.max_exclusive,
                        minInclusive=parameter.min_inclusive,
                        maxInclusive=parameter.max_inclusive,
                        step=parameter.step,
                        *[
                            PARAM("Option", value=option.value, label=option.label)
                            for option in parameter.options
                        ]
                    )
                    for parameter in url.parameters
                ],
                template=url.template,
                type=url.type,
                rel=url.rel if url.rel != "results" else None,
                indexOffset=url.index_offset if url.index_offset != 1 else None,
                pageOffset=url.page_offset if url.page_offset != 1 else None,
                **{
                    f"{{{NS_PARAM}}}method": url.method.value if url.method != HttpMethod.GET else None,
                    f"{{{NS_PARAM}}}enctype": url.enctype,
                }
            )
            for url in description.urls
        ] + [
            OS("Tags", " ".join(description.tags)) if description.tags else None,
        ] + [
            OS(
                "Image",
                width=image.width,
                height=image.height,
                type=image.type,
            )
            for image in description.images
        ] + [
            OS("LongName", description.long_name) if description.long_name else None,
            OS("Contact", description.contact) if description.contact else None,
        ] + [
            OS(
                "Query",
                role=query.role,
                title=query.title,
                totalResults=query.total_results,
                searchTerms=query.search_terms,
                count=query.count,
                startIndex=query.start_index,
                startPage=query.start_page,
                language=query.language,
                inputEncoding=query.input_encoding,
                outputEncoding=query.output_encoding,
                **{
                    f"{{{name[0]}}}{name[1]}" if name[0] is not None else name[1]: value
                    for name, value in query.extra_parameters.items()
                },
            )
            for query in description.queries
        ] + [
            OS("Developer", description.developer) if description.developer else None,
            OS("Attribution", description.attribution) if description.attribution else None,
            OS("SyndicationRight", description.syndication_right.value) if description.syndication_right != SyndicationRight.open else None,
            OS("AdultContent", "true") if description.adult_content else None,
        ] + ([
            OS("Language", language)
            for language in description.languages
        ] if description.languages != ["*"] else []) + ([
            OS("InputEncoding", input_encoding)
            for input_encoding in description.input_encodings
        ] if description.input_encodings != ["UTF-8"] else []) + ([
            OS("OutputEncoding", output_encoding)
            for output_encoding in description.output_encodings
        ] if description.output_encodings != ["UTF-8"] else []))
    )
