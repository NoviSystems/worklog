from django import template
register = template.Library()


@register.filter
def verbose_name(model_set, field):
    return model_set[0]._meta.get_field(field).verbose_name.title()
