from datetime import datetime
from typing import BinaryIO, Tuple, Union

from pygml.georss import parse_georss, NAMESPACE as NS_GEORSS

from .osdd11 import NS_OSDD
from .result import SearchResultItem, SearchResultPage
from .utils import parse_datetime, unwrap
from .xml import parse_xml, unwrap_element


NS_ATOM = "http://www.w3.org/2005/Atom"
NS_DC = "http://purl.org/dc/elements/1.1/"

NAMESPACES = {
    "atom": NS_ATOM,
    "os": NS_OSDD,
    "dc": NS_DC,
    "georss": NS_GEORSS,
}


def parse_temporal(value: str) -> Union[datetime, Tuple[datetime, datetime]]:
    if "/" in value:
        start, end = (parse_datetime(part) for part in value.split("/"))
        return (start, end)
    return parse_datetime(value)


def parse_atom_feed(source: Union[BinaryIO, bytes]) -> SearchResultPage:
    root = parse_xml(source, (NS_ATOM, "feed"))
    return SearchResultPage(
        title=root.findtext("atom:title", namespaces=NAMESPACES),
        id=root.findtext("atom:id", namespaces=NAMESPACES),
        source=root.findtext("atom:link[@rel='search']", namespaces=NAMESPACES),
        total_results=int(root.findtext("os:totalResults", namespaces=NAMESPACES)),
        start_index=int(root.findtext("os:startIndex", namespaces=NAMESPACES)),
        items_per_page=int(root.findtext("os:itemsPerPage", namespaces=NAMESPACES)),
        items=[
            SearchResultItem(
                title=entry.findtext("atom:title", namespaces=NAMESPACES),
                id=entry.findtext("atom:id", namespaces=NAMESPACES),
                identifier=entry.findtext("dc:identifier", namespaces=NAMESPACES),
                creator=entry.findtext("atom:creator", namespaces=NAMESPACES),
                subjects=[
                    category.attrib["term"]
                    for category in entry.findall("atom:category", NAMESPACES)
                ],
                abstract=entry.findtext("atom:summary", namespaces=NAMESPACES),
                contributors=[
                    contributor.text
                    for contributor in entry.findall("atom:contributor", NAMESPACES)
                ],
                modified=unwrap(
                    entry.findtext("atom:updated", namespaces=NAMESPACES),
                    parse_temporal,
                ),
                date=unwrap(
                    entry.findtext("dc:date", namespaces=NAMESPACES), parse_temporal
                ),
                sources=[
                    source.text
                    for source in entry.findall("atom:link[@rel='via']", NAMESPACES)
                ],
                language=entry.findtext("atom:language", namespaces=NAMESPACES),
                rights=entry.findtext("atom:rights", namespaces=NAMESPACES),
                envelope=unwrap(
                    entry.find("georss:*", NAMESPACES), parse_georss
                ),
            )
            for entry in root.findall("atom:entry", NAMESPACES)
        ],
        creator=root.findtext("atom:creator", namespaces=NAMESPACES),
        subjects=[
            category.text for category in root.findall("atom:category", NAMESPACES)
        ],
        abstract=root.findtext("atom:summary", namespaces=NAMESPACES),
        publisher=root.findtext("atom:generator", namespaces=NAMESPACES),
        contributors=[
            contributor.text
            for contributor in root.findall("atom:contributor", NAMESPACES)
        ],
        modified=unwrap(
            root.findtext("atom:updated", namespaces=NAMESPACES), parse_temporal
        ),
        identifier=root.findtext("dc:identifier", namespaces=NAMESPACES),
        language=root.findtext("atom:language", namespaces=NAMESPACES),
        rights=root.findtext("atom:rights", namespaces=NAMESPACES),
        envelopes=[],
        next_page=unwrap_element(
            root.find("atom:link[@rel='next']", namespaces=NAMESPACES),
            lambda l: l.attrib["href"],
        ),
        previous_page=unwrap_element(
            root.find(
                "atom:link[@rel='prev'] | atom:link[@rel='previous']",
                namespaces=NAMESPACES,
            ),
            lambda l: l.attrib["href"],
        ),
        first_page=unwrap_element(
            root.find("atom:link[@rel='first']", namespaces=NAMESPACES),
            lambda l: l.attrib["href"],
        ),
        last_page=unwrap_element(
            root.find("atom:link[@rel='last']", namespaces=NAMESPACES),
            lambda l: l.attrib["href"],
        ),
    )
