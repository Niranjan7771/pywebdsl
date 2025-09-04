from pywebdsl import html, css

# 1. Define the animation stages using the new keyframes method
css.keyframes("fade-and-slide-in", {
    "0%": {
        "opacity": "0",
        "transform": "translateY(20px)"
    },
    "100%": {
        "opacity": "1",
        "transform": "translateY(0)"
    }
})

# 2. Apply the animation to an element
css.rule(".animated-heading", {
    "animation": "fade-and-slide-in 1.5s ease-out forwards"
})

# 3. Create the HTML content
with html.body():
    html.h1("This heading will animate!", class_="animated-heading")
    html.p(
        "This is a demonstration of creating CSS animations using Python.",
        style="animation-delay: 1s; opacity: 0;", # Inline style for delayed animation
        class_="animated-heading" 
    )