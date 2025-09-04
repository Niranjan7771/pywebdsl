from pywebdsl import html, css

with html.body():
    html.h1("Homepage")
    html.p("This is the main page.")
    # Use the new helper function
    html.a("About Page", href=url_for("about.py"))
    html.a("Contact Form", href=url_for("contact/form.py"))