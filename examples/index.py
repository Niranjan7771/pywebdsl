from pywebdsl import html, css

with html.body():
    with html.div(class_="container"):
        html.h1("Homepage")
        html.p("Welcome to the main page of our website.")
        html.a("Go to the About page", href="about.html")

css.rule(".container", {
    "font-family": "sans-serif",
    "max-width": "800px",
    "margin": "0 auto",
    "padding": "2rem"
})

css.rule("h1", {
    "color": "darkblue"
})