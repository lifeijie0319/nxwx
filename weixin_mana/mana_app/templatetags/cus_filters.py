# -*- coding: utf-8 -*-
from django import template
from django.template.defaultfilters import stringfilter


register = template.Library()

@register.filter
@stringfilter
def add_pre(value, prefix):
    return prefix + value


@register.filter
def invert(value):
    return -value


@register.filter
def dtime_minus(end, start):
    if end:
        interval = str(end - start)
        interval = ':'.join(interval.split(':')[:2])
    else:
        interval = ''
    return interval
