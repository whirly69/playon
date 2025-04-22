from django import template
from matches.models import MatchConvocation
from django.utils.safestring import mark_safe
register = template.Library()

@register.filter
def get_item(dictionary, key):
    try:
        return dictionary.get(key)
    except AttributeError:
        return None
@register.filter
def is_player_of_group(user, group):
    return user.player_set.filter(group=group).exists()
@register.filter
def is_convocated(match, user):
    return match.matchconvocation_set.filter(player__user=user).exists()
@register.filter
def get_player_id_for_group(user, group):
    player = user.player_set.filter(group=group).first()
    return player.id if player else None
@register.filter
def str_replace(value, args):
    old, new = args.split(',')
    return value.replace(old, new)
@register.filter
def is_confirmed_convocated(user, match):
    return MatchConvocation.objects.filter(match=match, player__user=user, status='confirmed').exists()