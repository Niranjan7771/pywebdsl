# pywebdsl/compiler.py

"""
pywebdsl.compiler
-----------------
Takes the recorded DOM and CSS from the DSL runtime and generates pretty HTML/CSS.
"""

import inspect
from html import escape as _escape

def _attrs_to_str(attrs, event_handlers=None):
    if not attrs and not event_handlers:
        return ""
    
    parts = []
    # Regular attributes
    for k, v in (attrs or {}).items():
        if v is True:
            parts.append(k)
        elif v is False or v is None:
            continue
        else:
            parts.append(f'{k}="{_escape(str(v), quote=True)}"')
            
    # NEW: Event handler attributes
    for k, func in (event_handlers or {}).items():
        # The value is the Python function name, which Brython will call
        parts.append(f'{k}="{func.__name__}()"')
        
    return " " + " ".join(parts) if parts else ""

def _render_node(node, indent=0):
    pad = "  " * indent
    # Pass event handlers to the attribute string function
    attrs = _attrs_to_str(node.attrs, node.event_handlers)
    
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
            # Handle self-closing tags if desired, for now, all have closing tags
            return f"{pad}<{node.tag}{attrs}></{node.tag}>"


# NEW: Function to generate the Python script block for Brython
def _generate_python_script(scripts):
    if not scripts:
        return ""

    # Header for Brython
    script_lines = [
        '<script type="text/python">',
        'from browser import document, alert, console',
        ''
    ]
    
    # Extract the source code of each function
    for func in scripts:
        try:
            source = inspect.getsource(func)
            script_lines.append(source)
        except (TypeError, OSError) as e:
            print(f"Warning: Could not get source for {func.__name__}: {e}")

    script_lines.append('</script>')
    return "\n".join(script_lines)


def generate_html(roots, event_scripts=None):
    # If there is no explicit <html>, wrap in a basic scaffold
    body_str = "\n".join(_render_node(n, 2) for n in roots)
    
    # Generate the Python script block
    python_script_block = _generate_python_script(event_scripts or [])

    # Check if onload="brython()" is already on the body tag
    has_brython_onload = any(
        node.tag == 'body' and 'onload' in node.attrs and 'brython()' in node.attrs['onload']
        for node in roots
    )
    
    body_tag_start = '  <body onload="brython()">' if not has_brython_onload else '  <body>'


    doc = [
        "<!DOCTYPE html>",
        "<html>",
        "  <head>",
        '    <meta charset="utf-8">',
        "    <title>PyWeb-DSL</title>",
        '    <link rel="stylesheet" href="styles.css">',
        '    ',
        '    <script src="https://cdn.jsdelivr.net/npm/brython@3.11.2/brython.min.js"></script>',
        '    <script src="https://cdn.jsdelivr.net/npm/brython@3.11.2/brython_stdlib.js"></script>',
        "  </head>",
        body_tag_start,
        body_str,
        "",
        "    ",
        f"    {python_script_block}",
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