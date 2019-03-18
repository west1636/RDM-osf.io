from django import template

from admin.base.utils import reverse_qs

register = template.Library()


@register.simple_tag
def reverse_list(*args, **kwargs):
    return reverse_qs('institutions:institution_user_list_filter', query_kwargs=kwargs)

