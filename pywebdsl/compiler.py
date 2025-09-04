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
    for k, v in (attrs or {}).items():
        if v is True: parts.append(k)
        elif v is False or v is None: continue
        else: parts.append(f'{k}="{_escape(str(v), quote=True)}"')
    for k, func in (event_handlers or {}).items():
        parts.append(f'{k}="{func.__name__}()"')
    return " " + " ".join(parts) if parts else ""

def _render_node(node, indent=0):
    pad = "  " * indent
    attrs = _attrs_to_str(node.attrs, node.event_handlers)
    if node.children:
        open_tag = f"{pad}<{node.tag}{attrs}>"
        inner = [("  " * (indent + 1) + _escape(node.text))] if node.text else []
        inner.extend(_render_node(child, indent + 1) for child in node.children)
        close_tag = f"{pad}</{node.tag}>"
        return "\n".join([open_tag] + inner + [close_tag])
    else:
        if node.text: return f"{pad}<{node.tag}{attrs}>{_escape(node.text)}</{node.tag}>"
        else: return f"{pad}<{node.tag}{attrs}></{node.tag}>"

def _generate_python_script(scripts):
    if not scripts: return ""
    script_lines = ['<script type="text/python">', 'from browser import document, alert, console', '']
    for func in scripts:
        try:
            script_lines.append(inspect.getsource(func))
        except (TypeError, OSError) as e:
            print(f"Warning: Could not get source for {func.__name__}: {e}")
    script_lines.append('</script>')
    return "\n".join(script_lines)

def generate_html(roots, event_scripts=None, css_path="styles.css"):
    body_str = "\n".join(_render_node(n, 2) for n in roots)
    python_script_block = _generate_python_script(event_scripts or [])
    has_onload = any(n.tag == 'body' and 'onload' in n.attrs and 'brython()' in n.attrs['onload'] for n in roots)
    body_tag_start = '  <body onload="brython()">' if not has_onload else '  <body>'
    doc = [
        "<!DOCTYPE html>", "<html>", "  <head>", '    <meta charset="utf-8">',
        "    <title>PyWeb-DSL</title>", f'    <link rel="stylesheet" href="{css_path}">',
        '    <script src="https://cdn.jsdelivr.net/npm/brython@3.11.2/brython.min.js"></script>',
        '    <script src="https://cdn.jsdelivr.net/npm/brython@3.11.2/brython_stdlib.js"></script>',
        "  </head>", body_tag_start, body_str, "",
        f"    {python_script_block}", "  </body>", "</html>"
    ]
    return "\n".join(doc)

def generate_css(rules, keyframes):
    lines = []
    
    # NEW: Generate @keyframes rules first
    if keyframes:
        for name, stages in keyframes.items():
            lines.append(f"@keyframes {name} {{")
            for stage, props in stages.items():
                lines.append(f"  {stage} {{")
                for k, v in props.items():
                    lines.append(f"    {k}: {v};")
                lines.append("  }")
            lines.append("}")
            lines.append("")
        
    # Generate regular style rules
    for selector, props in rules.items():
        lines.append(f"{selector} {{")
        for k, v in props.items():
            lines.append(f"  {k}: {v};")
        lines.append("}")
        lines.append("")
        
    return "\n".join(lines).rstrip() + ("\n" if rules or keyframes else "")