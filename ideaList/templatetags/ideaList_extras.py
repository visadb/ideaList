# -*- coding: utf-8 -*-

from django import template
register = template.Library()

def escape_utf8_scands(value):
    return value.replace(u'å','&aring;').replace(u'Å','&Aring;').replace(u'ä','&auml;').replace(u'Ä','&Auml;').replace(u'ö','&ouml;').replace(u'Ö','&Ouml;')
register.filter('escape_utf8_scands', escape_utf8_scands)
