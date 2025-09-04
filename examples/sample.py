from pywebdsl import html, css

with html.body():
    with html.div(class_="box"):
        html.h1("Dashboard")
        html.p("Welcome to the system")

css.rule(".box", {
    "color": "blue",
    "padding": "20px"
})
