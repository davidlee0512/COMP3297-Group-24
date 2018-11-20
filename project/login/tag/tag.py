from django import template

register = template.Library()

@register.filter
def getCombinedWeight(value):
    return value.getCombinedWeight()