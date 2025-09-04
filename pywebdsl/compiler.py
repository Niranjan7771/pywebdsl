\
"""
pywebdsl.compiler
-----------------
Takes the recorded DOM and CSS from the DSL runtime and generates pretty HTML/CSS.
"""

from html import escape as _escape

def _attrs_to_str(attrs):
    if not attrs:
        return ""
    parts = []
    for k, v in attrs.items():
        if v is True:
            parts.append(k)
        elif v is False or v is None:
            continue
        else:
            parts.append(f'{k}="{_escape(str(v), quote=True)}"')
    return " " + " ".join(parts) if parts else ""

def _render_node(node, indent=0):
    pad = "  " * indent
    attrs = _attrs_to_str(node.attrs)
    if node.children:
        open_tag = f"{pad}<{node.tag}{attrs}>"
        inner = []
        if node.text:
            inner.append("  " * (indent + 1) + _escape(node.text))
        for child in node.children:
            inner.append(_render_node(child, indent + 1))
        close_tag = f"{pad}</{node.tag}>"
        return "\n".join([open_tag] + inner + [close_tag])
    else:
        if node.text:
            return f"{pad}<{node.tag}{attrs}>{_escape(node.text)}</{node.tag}>"
        else:
            return f"{pad}<{node.tag}{attrs}></{node.tag}>"

def generate_html(roots):
    # If there is no explicit <html>, wrap in a basic scaffold
    body_str = "\n".join(_render_node(n, 2) for n in roots)
    doc = [
        "<!DOCTYPE html>",
        "<html>",
        "  <head>",
        '    <meta charset="utf-8">',
        "    <title>PyWeb-DSL</title>",
        '    <link rel="stylesheet" href="styles.css">',
        "  </head>",
        "  <body>",
        body_str,
        "  </body>",
        "</html>"
    ]
    return "\n".join(doc)

def generate_css(rules):
    lines = []
    for selector, props in rules.items():
        lines.append(f"{selector} {{")
        for k, v in props.items():
            lines.append(f"  {k}: {v};")
        lines.append("}")
        lines.append("")
    return "\n".join(lines).rstrip() + ("\n" if rules else "")
