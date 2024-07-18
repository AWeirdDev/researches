from typing import Optional, Union

from selectolax.lexbor import LexborNode
from selectolax.parser import Node


def textof(
    node: Optional[Union[LexborNode, Node]],
    *,
    deep: bool = True,
    separator: str = "",
    strip: bool = False,
) -> str:
    return node.text(deep=deep, separator=separator, strip=strip) if node else ""


def some(node: Optional[Union[LexborNode, Node]]):
    return node if node else LexborNode()
