from django import template

register = template.Library()

@register.filter
def dict_get(d, key):
    """
    Permette di accedere a un valore di un dizionario in un template:
    {{ my_dict|dict_get:key }}
    """
    if isinstance(d, dict):
        return d.get(key)
    return None
