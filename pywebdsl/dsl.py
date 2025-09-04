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
        self.event_handlers = event_handlers or {} 

    def append(self, child):
        self.children.append(child)

    def __repr__(self):
        return f"Node(tag={self.tag!r}, attrs={self.attrs!r}, text={self.text!r}, children={len(self.children)})"


class HTMLNamespace:
    _stack = []
    _roots = []
    _event_scripts = set()
    _known_tags = {
        "html", "head", "body",
        "div", "span", "p", "h1", "h2", "h3", "ul", "li",
        "a", "img", "section", "article", "header", "footer",
        "button", "input", "label", "script"
    }
    _event_attrs = {
        "onclick", "onsubmit", "oninput", "onchange", "onmouseover", "onload"
    }

    def reset(self):
        self._stack.clear()
        self._roots.clear()
        self._event_scripts.clear()

    def _normalize_attrs(self, attrs):
        if "class_" in attrs:
            attrs["class"] = attrs.pop("class_")
        return attrs

    def __getattr__(self, tag):
        if tag not in self._known_tags:
            pass

        def tag_callable(*args, **kwargs):
            kwargs = self._normalize_attrs(kwargs)
            text = None
            if args and isinstance(args[0], str):
                text = args[0]
            
            event_handlers = {}
            regular_attrs = {}
            for k, v in kwargs.items():
                if k in self._event_attrs and callable(v):
                    event_handlers[k] = v
                    self._event_scripts.add(v)
                else:
                    regular_attrs[k] = v

            node = Node(tag, attrs=regular_attrs, text=text, event_handlers=event_handlers)

            if self._stack:
                self._stack[-1].append(node)
            else:
                self._roots.append(node)

            return node
        tag_callable.__name__ = tag
        return tag_callable

    @contextmanager
    def _ctx(self, tag, *args, **kwargs):
        node = self.__getattr__(tag)(*args, **kwargs)
        self._stack.append(node)
        try:
            yield node
        finally:
            self._stack.pop()

    def body(self, *args, **kwargs): return self._ctx("body", *args, **kwargs)
    def div(self, *args, **kwargs): return self._ctx("div", *args, **kwargs)
    def ul(self, *args, **kwargs): return self._ctx("ul", *args, **kwargs)
    def li(self, *args, **kwargs): return self._ctx("li", *args, **kwargs)
    def section(self, *args, **kwargs): return self._ctx("section", *args, **kwargs)
    def article(self, *args, **kwargs): return self._ctx("article", *args, **kwargs)

    @property
    def roots(self): return list(self._roots)
    @property
    def event_scripts(self): return list(self._event_scripts)


class CSSNamespace:
    """
    Records CSS rules and @keyframes as mappings.
    """
    def __init__(self):
        self._rules = {}
        self._keyframes = {} # NEW: To store keyframe definitions

    def reset(self):
        self._rules.clear()
        self._keyframes.clear() # NEW: Reset keyframes

    def rule(self, selector, props):
        if not isinstance(props, dict):
            raise TypeError("css.rule expects a dict of properties")
        norm = {k: str(v) for k, v in props.items()}
        self._rules.setdefault(selector, {}).update(norm)

    # NEW: Method to define a @keyframes animation
    def keyframes(self, name, stages):
        if not isinstance(stages, dict):
            raise TypeError("css.keyframes expects a dict of stages")
        # Normalize the properties within each stage
        norm_stages = {}
        for stage, props in stages.items():
            if not isinstance(props, dict):
                raise TypeError(f"Stage '{stage}' in keyframes '{name}' must be a dict")
            norm_stages[stage] = {k: str(v) for k, v in props.items()}
        self._keyframes[name] = norm_stages

    @property
    def rules(self): return {k: dict(v) for k, v in self._rules.items()}
    @property
    def keyframes_data(self): return dict(self._keyframes) # NEW: Accessor for keyframes


# Singletons used by user programs
html = HTMLNamespace()
css = CSSNamespace()