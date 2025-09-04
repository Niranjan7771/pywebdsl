# PyWeb-DSL (mini project scaffold)

Write HTML and CSS in a Pythonic DSL:

```python
# examples/sample.py
from pywebdsl import html, css

with html.body():
    with html.div(class_="box"):
        html.h1("Dashboard")
        html.p("Welcome to the system")

css.rule(".box", {
    "color": "blue",
    "padding": "20px"
})
```

## Run

```bash
# 1) Put this folder on your PYTHONPATH or install locally
# 2) Execute the CLI with your script:
python pywebdsl_cli.py examples/sample.py
```

This will generate `index.html` and `styles.css` and open the page in your default browser.
