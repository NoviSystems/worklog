from django import template
register = template.Library()


# The following was taken from:
#       django/contrib/admin/templatetags/admin_list.py
# This is nearly identical to the cited code.  This is used by our overridden
# admin template.
@register.inclusion_tag('admin/worklog/workitem/actions.html', takes_context=True)
def workitem_admin_actions(context):
    """
    Track the number of times the action field has been rendered on the page,
    so we know which value to use.
    """
    context['action_index'] = context.get('action_index', -1) + 1
    return context


@register.filter
def verbose_name(model_set, field):
    return model_set[0]._meta.get_field(field).verbose_name.title()
