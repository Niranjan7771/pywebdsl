#!/usr/bin/env python3
"""
pywebdsl_cli.py
Run a PyWeb-DSL script and open the generated page.
Usage:
    python pywebdsl_cli.py examples/sample.py --out build --no-open
"""
import argparse
from pathlib import Path
from pywebdsl.runtime import run_script

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("script", help="Path to your DSL .py script")
    ap.add_argument("--out", default=None, help="Output directory for index.html/styles.css")
    ap.add_argument("--no-open", action="store_true", help="Do not open browser automatically")
    args = ap.parse_args()

    script = Path(args.script)
    if not script.exists():
        ap.error(f"Script not found: {script}")

    result = run_script(script, out_dir=args.out, open_browser=not args.no_open)
    if isinstance(result, tuple):
        index_path, css_path = result
        print("HTML:", index_path)
        print("CSS :", css_path)
    else:
        print("Opened:", result)

if __name__ == "__main__":
    main()
