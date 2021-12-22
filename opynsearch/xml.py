from io import BytesIO
from typing import BinaryIO, Optional, Tuple, Union

from lxml.etree import QName, parse, _Element as Element, _ElementTree as ElementTree
from lxml.builder import ElementMaker as LxmlElementMaker


__all__ = ["ElementMaker", "Element", "parse_xml"]


class ElementMaker(LxmlElementMaker):
    """
    Custom ElementMaker subclass to gracefully handle `None`s in child
    elements and attributes
    """
    def __call__(self, tag, *children, **attrib):
        children = [child for child in children if child is not None]
        attrib = {k: v for k, v in attrib.items() if v is not None}
        return super().__call__(tag, *children, **attrib)


def parse_xml(source: Union[BinaryIO, bytes], expected_root_tag: Optional[Tuple[str, str]] = None) -> Element:
    if isinstance(source, bytes):
        source = BytesIO(source)
    tree: Union[Element, ElementTree] = parse(source)
    root = tree if isinstance(tree, Element) else tree.getroot()

    if expected_root_tag and QName(root) != QName(*expected_root_tag):
        raise ValueError(f"Node {root} is not allowed. Expected {expected_root_tag}")

    return root
