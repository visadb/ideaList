# -*- coding: utf-8 -*-

from django import template
register = template.Library()

@register.filter
def escape_utf8_scands(value):
    return value.replace(u'å','&aring;').replace(u'Å','&Aring;').replace(u'ä','&auml;').replace(u'Ä','&Auml;').replace(u'ö','&ouml;').replace(u'Ö','&Ouml;')

@register.filter
def get_range(n):
    return range(n)

@register.filter
def multiply(a, b):
    return int(a) * int(b)
