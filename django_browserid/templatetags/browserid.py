from django import template

from django_browserid import helpers


register = template.Library()


@register.simple_tag
def browserid_info(**kwargs):
    return helpers.browserid_info(**kwargs)


@register.simple_tag
def browserid_login(**kwargs):
    return helpers.browserid_login(**kwargs)


@register.simple_tag
def browserid_logout(**kwargs):
    return helpers.browserid_logout(**kwargs)


@register.simple_tag
def browserid_js(**kwargs):
    return helpers.browserid_js(**kwargs)

@register.simple_tag
def browserid_css(**kwargs):
    return helpers.browserid_css(**kwargs)
