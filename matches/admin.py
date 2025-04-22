from django.contrib import admin
from .models import Match, MatchConvocation, MatchTeamAssignment, MatchPerformance, MatchComment, MatchMVPVote

class MatchTeamAssignmentAdmin(admin.ModelAdmin):
    model=MatchTeamAssignment
    list_display=['id','match','player','team','vote']
    list_filter=['match','team']
    search_fields=['match__group__name','player__name']

class MatchPerformanceAdmin(admin.ModelAdmin):
    model=MatchPerformance
    list_display=['id','match','player','goals']
    
class MatchAdmin(admin.ModelAdmin):
    model=MatchPerformance
    list_display=['id','group','date','time','structure','players_per_team','is_public', 'is_cancelled','created_by','created_at','score_team1','score_team2']
    list_filter=['group','date','time','structure','players_per_team']

class MatchConvocationAdmin(admin.ModelAdmin):
    model=MatchConvocation
    list_display=['id','match','player','status']
    list_filter=['match','player','status']
    search_fields=['match__group__name','player__name']

class MatchCommentAdmin(admin.ModelAdmin):
    model=MatchComment
    list_display=['id','match','author','content']
    list_filter=['match','author']
    search_fields=['match__group__name','author__username']
    list_editable=['content']

class MatchMVPVoteAdmin(admin.ModelAdmin):
    model=MatchMVPVote
    list_display=['id','match','voter','voted_player']
    list_filter=['match','voter','voted_player']    
    search_fields=['match__group__name','voter__username','voted_player__name']
    list_display_links=['id','match','voter']
    list_select_related=['match','voter','voted_player']

admin.site.register(Match,MatchAdmin)
admin.site.register(MatchConvocation,MatchConvocationAdmin)
admin.site.register(MatchTeamAssignment,MatchTeamAssignmentAdmin)
admin.site.register(MatchPerformance,MatchPerformanceAdmin)
admin.site.register(MatchComment,MatchCommentAdmin)
admin.site.register(MatchMVPVote,MatchMVPVoteAdmin)

