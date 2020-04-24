"""
This is extracted from the unmaintained https://github.com/jazzband/django-floppyforms to provide a datalist widget.
It has not been cleaned up yet.
"""

from django import forms
from django.template import Context, loader
from django.utils import formats
from django.utils.encoding import force_text


class DictContext(dict):
    pass


REQUIRED_CONTEXT_ATTRIBTUES = (
    "_form_config",
    "_form_render",
)


def flatten_context(context):
    if isinstance(context, Context):
        flat = {}
        for d in context.dicts:
            flat.update(d)
        return flat
    else:
        return context


def flatten_contexts(*contexts):
    """Takes a list of context instances and returns a new dict that
    combines all of them."""
    new_context = DictContext()
    for context in contexts:
        if context is not None:
            new_context.update(flatten_context(context))
            for attr in REQUIRED_CONTEXT_ATTRIBTUES:
                if hasattr(context, attr):
                    setattr(new_context, attr, getattr(context, attr))
    return new_context


class Widget(forms.Widget):
    is_required = False

    def render(self, name, value, attrs=None, renderer=None):
        """
        Returns this Widget rendered as HTML, as a Unicode string.
        The 'value' given is not guaranteed to be valid input, so subclass
        implementations should program defensively.
        """
        raise NotImplementedError("subclasses of Widget must provide a render() method")

    def build_attrs(self, extra_attrs=None, **kwargs):
        """
        Backported from Django 1.10
        Helper function for building an attribute dictionary.
        """
        attrs = dict(self.attrs, **kwargs)
        if extra_attrs:
            attrs.update(extra_attrs)
        return attrs

    # Backported from Django 1.7
    @property
    def is_hidden(self):
        return self.input_type == "hidden" if hasattr(self, "input_type") else False

    # Backported from Django 1.9
    if not hasattr(forms.Widget, "format_value"):

        def format_value(self, value):
            return self._format_value(value)


class Input(Widget):
    template_name = "widgets/input.html"
    input_type = None
    datalist = None

    def __init__(self, *args, **kwargs):
        datalist = kwargs.pop("datalist", None)
        if datalist is not None:
            self.datalist = datalist
        template_name = kwargs.pop("template_name", None)
        if template_name is not None:
            self.template_name = template_name
        super(Input, self).__init__(*args, **kwargs)
        # This attribute is used to inject a surrounding context in the
        # floppyforms templatetags, when rendered inside a complete form.
        self.context_instance = None

    def get_context_data(self):
        return {}

    def format_value(self, value):
        if self.is_localized:
            value = formats.localize_input(value)
        return force_text(value)

    def get_context(self, name, value, attrs=None):
        context = {
            "widget": self,
            "type": self.input_type,
            "name": name,
            "hidden": self.is_hidden,
            "required": self.is_required,
            "True": True,
        }

        # True is injected in the context to allow stricter comparisons
        # for widget attrs. See #25.
        if self.is_hidden:
            context["hidden"] = True

        if value is None:
            value = ""

        if value != "":
            # Only add the value if it is non-empty
            context["value"] = self.format_value(value)

        context.update(self.get_context_data())
        context["attrs"] = self.build_attrs(attrs)

        for key, attr in context["attrs"].items():
            if attr == 1:
                # 1 == True so 'key="1"' will show up only as 'key'
                # Casting to a string so that it doesn't equal to True
                # See #25.
                if not isinstance(attr, bool):
                    context["attrs"][key] = str(attr)

        if self.datalist is not None:
            context["datalist"] = self.datalist
        return context

    def render(self, name, value, attrs=None, **kwargs):
        template_name = kwargs.pop("template_name", None)
        if template_name is None:
            template_name = self.template_name
        context = self.get_context(name, value, attrs=attrs or {})
        context = flatten_contexts(self.context_instance, context)
        return loader.render_to_string(template_name, context)


class TextInput(Input):
    template_name = "widgets/text.html"
    input_type = "text"

    def __init__(self, *args, **kwargs):
        if kwargs.get("attrs", None) is not None:
            self.input_type = kwargs["attrs"].pop("type", self.input_type)
        super(TextInput, self).__init__(*args, **kwargs)
