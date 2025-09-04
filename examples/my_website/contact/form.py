from pywebdsl import html, css

with html.body():
    html.h1("Contact Us")
    html.p("This page is in a subfolder.")
    # The helper automatically calculates the correct "../" path
    html.a("Go Home", href=url_for("index.py"))