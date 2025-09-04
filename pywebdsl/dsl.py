# pywebdsl/dsl.py

"""
pywebdsl.dsl
------------
A tiny Python-embedded DSL to write HTML/CSS using context managers and function calls.
This runtime records a DOM-like tree and CSS rules during normal Python execution.
"""
import inspect
from contextlib import contextmanager

class Node:
    def __init__(self, tag, attrs=None, text=None, event_handlers=None):
        self.tag = tag
        self.attrs = attrs or {}
        self.text = text
        self.children = []
        self.event_handlers = event_handlers or {} # NEW: Store event handlers

    def append(self, child):
        self.children.append(child)

    def __repr__(self):
        return f"Node(tag={self.tag!r}, attrs={self.attrs!r}, text={self.text!r}, children={len(self.children)})"


class HTMLNamespace:
    """
    Provides attributes like html.div, html.h1, etc.
    Each attribute is a callable to create a Node immediately (for leaf nodes)
    or usable as a context manager via 'with html.div(...): ...' to create nested nodes.
    """

    # A stack to track the current parent nodes during 'with' nesting
    _stack = []
    # A list of top-level nodes (commonly you'll start with body/html)
    _roots = []
    # NEW: A set to store all functions used as event handlers
    _event_scripts = set()


    # Default known singleton tags to support as leaf calls
    _known_tags = {
        "html", "head", "body",
        "div", "span", "p", "h1", "h2", "h3", "ul", "li",
        "a", "img", "section", "article", "header", "footer",
        "button", "input", "label", "script"
    }
    # NEW: Known event handler attributes
    _event_attrs = {
        "onclick", "onsubmit", "oninput", "onchange", "onmouseover", "onload"
    }

    def reset(self):
        self._stack.clear()
        self._roots.clear()
        self._event_scripts.clear()

    def _normalize_attrs(self, attrs):
        # Allow class_ to map to class for Python keyword compatibility
        if "class_" in attrs:
            attrs["class"] = attrs.pop("class_")
        return attrs

    def __getattr__(self, tag):
        # Dynamically create a tag callable/context-manager
        if tag not in self._known_tags:
            # allow any tag, but you can add validation if desired
            pass

        def tag_callable(*args, **kwargs):
            kwargs = self._normalize_attrs(kwargs)
            text = None
            if args and isinstance(args[0], str):
                text = args[0]
            
            # NEW: Separate event handlers from regular attributes
            event_handlers = {}
            regular_attrs = {}
            for k, v in kwargs.items():
                if k in self._event_attrs and callable(v):
                    event_handlers[k] = v
                    self._event_scripts.add(v)
                else:
                    regular_attrs[k] = v


            node = Node(tag, attrs=regular_attrs, text=text, event_handlers=event_handlers)

            # If we're inside a context, append to current parent; else treat as root or leaf
            if self._stack:
                self._stack[-1].append(node)
            else:
                self._roots.append(node)

            return node
        tag_callable.__name__ = tag
        return tag_callable

    @contextmanager
    def _ctx(self, tag, *args, **kwargs):
        # Internal helper to support 'with html.tag(...)'
        node = self.__getattr__(tag)(*args, **kwargs)
        self._stack.append(node)
        try:
            yield node
        finally:
            self._stack.pop()

    # Expose context managers for common tags:
    def body(self, *args, **kwargs):
        return self._ctx("body", *args, **kwargs)
    def div(self, *args, **kwargs):
        return self._ctx("div", *args, **kwargs)
    def ul(self, *args, **kwargs):
        return self._ctx("ul", *args, **kwargs)
    def li(self, *args, **kwargs):
        return self._ctx("li", *args, **kwargs)
    def section(self, *args, **kwargs):
        return self._ctx("section", *args, **kwargs)
    def article(self, *args, **kwargs):
        return self._ctx("article", *args, **kwargs)

    @property
    def roots(self):
        return list(self._roots)

    # NEW: Property to access the collected event handler functions
    @property
    def event_scripts(self):
        return list(self._event_scripts)


class CSSNamespace:
    """
    Records CSS rules as a mapping: selector -> {prop: value, ...}
    """
    def __init__(self):
        self._rules = {}

    def reset(self):
        self._rules.clear()

    def rule(self, selector, props):
        if not isinstance(props, dict):
            raise TypeError("css.rule expects a dict of properties")
        # Normalize values to strings
        norm = {}
        for k, v in props.items():
            norm[k] = str(v)
        self._rules.setdefault(selector, {}).update(norm)

    @property
    def rules(self):
        return {k: dict(v) for k, v in self._rules.items()}


# Singletons used by user programs
html = HTMLNamespace()
css = CSSNamespace()