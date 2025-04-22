from django.contrib import admin
from .models import Notification
# Register your models here.
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('user__username', 'message')
    ordering = ('-created_at',)

admin.site.register(Notification, NotificationAdmin)