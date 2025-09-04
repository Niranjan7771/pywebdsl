from pywebdsl import html, css

with html.body():
    html.h1("About Us")
    html.p("This is the about page.")
    # Use the new helper function
    html.a("Go Home", href=url_for("index.py"))