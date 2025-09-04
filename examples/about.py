from pywebdsl import html, css

with html.body():
    with html.div(class_="container"):
        html.h1("About Us")
        html.p("This is the page where we talk about ourselves.")
        html.a("Go back home", href="index.html")

# These rules will be added to the same styles.css
css.rule("p", {
    "line-height": "1.6"
})