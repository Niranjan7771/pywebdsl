from pywebdsl import html, css

# 1. Define Python functions that will run in the browser
def show_alert():
    """Shows a simple browser alert."""
    alert("Hello from Python, running in your browser!")

def change_content():
    """Finds an element by ID and changes its text."""
    # The 'document' object is provided by Brython
    message_div = document["message_area"]
    message_div.text = "The content was updated by a Python function."
    message_div.style.color = "green"


# 2. Build the HTML structure
# The `onload="brython()"` is essential to initialize the Brython engine
with html.body(onload="brython()"):
    html.h1("Interactive Python Test")
    html.p("These buttons call Python functions that run in the browser.")
    
    # 3. Attach the Python functions to the `onclick` events
    html.button("Show an Alert", onclick=show_alert)
    html.button("Change Text Below", onclick=change_content)
    
    html.div("This is the initial text.", id="message_area")

# 4. Add some styling
css.rule("body", {
    "font-family": "sans-serif",
    "padding": "2rem"
})

css.rule("button", {
    "display": "block",
    "margin": "10px 0",
    "padding": "10px 15px",
    "cursor": "pointer"
})

css.rule("#message_area", {
    "margin-top": "20px",
    "padding": "15px",
    "border": "1px solid #ccc",
    "background-color": "#f0f0f0"
})