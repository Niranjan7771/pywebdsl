# pywebdsl_cli.py

import argparse
import runpy
import webbrowser
import os
from pathlib import Path

# Import the core components directly
from pywebdsl.dsl import html, css
from pywebdsl.compiler import generate_html, generate_css

def main():
    ap = argparse.ArgumentParser(description="Run PyWeb-DSL scripts in a directory to generate a static website.")
    ap.add_argument("input_dir", help="Path to the directory containing your .py scripts")
    ap.add_argument("--out", default="build", help="Output directory for the generated website")
    ap.add_argument("--no-open", action="store_true", help="Do not open the main page in a browser")
    args = ap.parse_args()

    input_dir = Path(args.input_dir).resolve()
    out_dir = Path(args.out).resolve()

    if not input_dir.is_dir():
        ap.error(f"Input directory not found: {input_dir}")

    print(f"Building site from '{input_dir}' into '{out_dir}'...")

    css.reset()
    scripts_found = []
    
    for script_path in sorted(input_dir.glob("**/*.py")):
        if "__pycache__" in script_path.parts: continue
        scripts_found.append(script_path)
        print(f"  - Processing: {script_path.relative_to(input_dir)}")
        
        html.reset()
        
        current_relative_dir = script_path.relative_to(input_dir).parent
        def url_for(target_path_str: str) -> str:
            target_relative_path = Path(target_path_str)
            path_from_current = os.path.relpath(target_relative_path, start=current_relative_dir)
            return str(Path(path_from_current).with_suffix(".html")).replace("\\", "/")

        runpy.run_path(str(script_path), init_globals={"html": html, "css": css, "url_for": url_for})

        relative_path = script_path.relative_to(input_dir)
        out_html_file = out_dir / relative_path.with_suffix(".html")
        depth = len(relative_path.parents) - 1
        relative_css_path = ("../" * depth) + "styles.css"

        html_str = generate_html(html.roots, html.event_scripts, css_path=relative_css_path)

        out_html_file.parent.mkdir(parents=True, exist_ok=True)
        out_html_file.write_text(html_str, encoding="utf-8")

    if not scripts_found:
        print("Warning: No .py scripts found in input directory.")
        return

    print(f"  - Generating shared stylesheet...")
    css_str = generate_css(css.rules, css.keyframes_data)
    css_path = out_dir / "styles.css"
    css_path.write_text(css_str, encoding="utf-8")
    
    print("\nBuild complete!")
    print(f"HTML pages and styles.css are in the '{out_dir}' directory.")

    # CORRECTED LINE: Use 'args.no_open' instead of 'args.no-open'
    if not args.no_open:
        main_page = out_dir / "index.html"
        if not main_page.exists() and scripts_found:
            main_page = out_dir / (scripts_found[0].relative_to(input_dir).with_suffix(".html"))
        if main_page.exists():
            print(f"Opening {main_page} in browser...")
            webbrowser.open(main_page.as_uri())

if __name__ == "__main__":
    main()