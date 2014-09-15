from django import template

register = template.Library()

@register.filter(name='count') 
def count(number):
	return range(number)

@register.filter(name='index')
def index(arr, i):
	return arr[i]

@register.filter(name='minus')
def plus(a, b):
	return a-b

@register.filter(name='times')
def times(a, b):
	return a*b