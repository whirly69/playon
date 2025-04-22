from django.contrib import admin
from .models import PlayerStats, PlayerVote

class PlayerStatsAdmin(admin.ModelAdmin):
    model=PlayerStats
    list_display=['id','player','group','presences','wins','draws','losses','goals','average_vote']
    list_display_links=['id','player','group']
    search_fields=['player__name','group__name']
    
class PlayerVoteAdmin(admin.ModelAdmin):
    model=PlayerVote
    list_display=['id','match','voter','voted_player','vote']
    list_display_links=['id','match','voter']
    search_fields=['match__id','voter__username','voted_player__name']

admin.site.register(PlayerStats,PlayerStatsAdmin)
admin.site.register(PlayerVote,PlayerVoteAdmin)
