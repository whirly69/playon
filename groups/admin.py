from django.contrib import admin
from .models import Group, Player, GroupJoinRequest, Role

class PlayerAdmin(admin.ModelAdmin):
    model = Player
    list_display = ['id', 'name','birth_date','role','group' ,'user']

class GroupJoinRequestAdmin(admin.ModelAdmin):
    model = GroupJoinRequest
    list_display = ['id', 'user', 'group', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['user__username', 'group__name']
   
admin.site.register(Group)
admin.site.register(Player, PlayerAdmin)
admin.site.register(GroupJoinRequest, GroupJoinRequestAdmin)
admin.site.register(Role)