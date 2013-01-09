from django import template

from fancy_tag import fancy_tag


register = template.Library()


@fancy_tag(register, takes_context=True)
def browserid_button(context, **kwargs):
    return context['browserid_button'](**kwargs)


@fancy_tag(register, takes_context=True)
def browserid_js(context, **kwargs):
    return context['browserid_js'](**kwargs)
