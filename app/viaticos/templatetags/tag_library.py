from django.template import Library

register = Library()
def to_int(value):
    return int(value)

register.filter("to_int",to_int)