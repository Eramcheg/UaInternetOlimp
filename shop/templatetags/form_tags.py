from django import template

register = template.Library()

@register.simple_tag
def get_field(form, field_name):
    print(form[field_name] if field_name in form.fields else '')
    return form[field_name] if field_name in form.fields else ''