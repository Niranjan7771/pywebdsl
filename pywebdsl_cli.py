# pywebdsl_cli.py

import argparse
import runpy
import webbrowser
from pathlib import Path

# Import the core components directly
from pywebdsl.dsl import html, css
from pywebdsl.compiler import generate_html, generate_css

def main():
    ap = argparse.ArgumentParser(
        description="Run PyWeb-DSL scripts in a directory to generate a static website."
    )
    ap.add_argument(
        "input_dir", help="Path to the directory containing your .py scripts"
    )
    ap.add_argument(
        "--out", default="build", help="Output directory for the generated website"
    )
    ap.add_argument(
        "--no-open", action="store_true", help="Do not open the main page in a browser"
    )
    args = ap.parse_args()

    # --- Setup ---
    input_dir = Path(args.input_dir)
    out_dir = Path(args.out)

    if not input_dir.is_dir():
        ap.error(f"Input directory not found: {input_dir}")

    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"Building site from '{input_dir}' into '{out_dir}'...")

    # --- HTML Generation Loop ---
    # Reset the shared CSS object once before the build.
    css.reset()
    
    scripts_found = []
    
    for script_path in sorted(input_dir.glob("*.py")):
        scripts_found.append(script_path)
        print(f"  - Processing: {script_path.name}")
        
        # 1. Reset the HTML builder for each new page.
        html.reset()

        # 2. Execute the user's script. CSS rules will be added to the shared css object.
        runpy.run_path(str(script_path), init_globals={"html": html, "css": css})

        # 3. Compile the HTML, now passing the event scripts as well.
        html_str = generate_html(html.roots, html.event_scripts)

        # 4. Write the HTML file.
        out_html_file = out_dir / (script_path.stem + ".html")
        out_html_file.write_text(html_str, encoding="utf-8")

    if not scripts_found:
        print("Warning: No .py scripts found in input directory.")
        return

    # --- CSS Generation (after all scripts have run) ---
    print(f"  - Generating shared stylesheet...")
    css_str = generate_css(css.rules)
    css_path = out_dir / "styles.css"
    css_path.write_text(css_str, encoding="utf-8")
    
    print("\nBuild complete!")
    print(f"HTML pages and styles.css are in the '{out_dir}' directory.")

    # --- Open in Browser ---
    if not args.no_open:
        main_page = out_dir / "index.html"
        if not main_page.exists() and scripts_found:
            main_page = out_dir / (scripts_found[0].stem + ".html")

        if main_page.exists():
            print(f"Opening {main_page} in browser...")
            webbrowser.open(main_page.resolve().as_uri())

if __name__ == "__main__":
    main()