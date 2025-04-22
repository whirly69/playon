from django import template

register = template.Library()

@register.filter
def dict_get(d, key):
    return d.get(key)

@register.filter
def is_player_of_group(user, group):
    return user.player_set.filter(group=group).exists()