from selectolax.parser import HTMLParser, Node

from .utils import textof


def get_markdown(html: str, target: str) -> str:
    """Gets Markdown.

    It may not look good if not formatted.

    Args:
        html (str): HTML string.
        target (str): CSS selector to the target. Used to unwrap the target.
    """
    parser = HTMLParser(html)
    n = parse_node_to_markdown(parser.css_first(target))
    n.unwrap()
    return parser.text().replace("\n\n\n", "\n\n").strip()


def parse_node_to_markdown(node: Node) -> Node:
    node.merge_text_nodes()
    replace_headings(node)

    for img in node.css("img"):
        img.replace_with("")

    for b in node.css("b"):
        b.replace_with(f"**{textof(b)}**")

    for br in node.css("br"):
        br.replace_with("\n\n")

    for p in node.css("p"):
        p.unwrap()

    for a in node.css("a"):
        a.replace_with(f"[{textof(a)}]({a.attributes.get('href', '/')})")

    for ul in node.css("ul"):
        texts = []
        for li in ul.css("li"):
            texts.append(f"- {textof(li, strip=True)}")

        ul.replace_with("\n".join(texts))

    for ol in node.css("ol"):
        texts = []
        for i, item in enumerate(ol.css("li")):
            texts.append(f"{i + 1}. {textof(item, strip=True)}")

        ol.replace_with("\n".join(texts))

    return node


def replace_headings(node: Node) -> None:
    for target in {"h1", "h2", "h3", "h4", "h5", "h6"}:
        for heading in node.css(target):
            heading.replace_with(f"{'#' * int(target[1])} {textof(heading)}")
