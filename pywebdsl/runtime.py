\
"""
pywebdsl.runtime
----------------
Convenience helpers: execute a user program that uses the DSL,
then generate HTML/CSS and optionally open it in the browser.
"""

import importlib.util
import runpy
import sys
import tempfile
import webbrowser
from pathlib import Path

from .dsl import html, css
from .compiler import generate_html, generate_css

def render_to_files(out_dir):
    """
    Use after the user's DSL script has executed.
    Writes index.html and styles.css to out_dir.
    Returns paths.
    """
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    html_str = generate_html(html.roots)
    css_str = generate_css(css.rules)
    (out / "index.html").write_text(html_str, encoding="utf-8")
    (out / "styles.css").write_text(css_str, encoding="utf-8")
    return out / "index.html", out / "styles.css"

def render_and_open(out_dir=None):
    """
    Renders to a temp directory (or provided dir) and opens in default browser.
    """
    if out_dir is None:
        tmp = Path(tempfile.mkdtemp(prefix="pywebdsl_"))
    else:
        tmp = Path(out_dir)
        tmp.mkdir(parents=True, exist_ok=True)
    index_path, _ = render_to_files(tmp)
    webbrowser.open(index_path.as_uri())
    return str(index_path)

def run_script(path, out_dir=None, open_browser=True):
    """
    Execute a user's DSL script in an isolated globals() dict where
    'html' and 'css' are available singletons that record DOM/CSS.
    Then render outputs.
    """
    # Reset singletons in case this is reused
    html.reset()
    css.reset()

    # Execute the script with a clean namespace that exposes our DSL
    ns = {"html": html, "css": css}
    runpy.run_path(str(path), init_globals=ns)

    if open_browser:
        return render_and_open(out_dir)
    else:
        index_path, css_path = render_to_files(out_dir or Path("."))
        return str(index_path), str(css_path)
