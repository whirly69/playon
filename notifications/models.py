from django.db import models
from django.conf import settings


class Notification(models.Model):
    match = models.ForeignKey("matches.Match", on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications' )
    message = models.TextField()
    link = models.URLField(blank=True, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Notifica"
        verbose_name_plural = "Notifiche"
        ordering = ['-created_at']

    def __str__(self):
        return f"Notifica per {self.user.username} - {'LETTA' if self.is_read else 'NON LETTA'}"
