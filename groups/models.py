from django.db import models
from django.conf import settings
from datetime import date



class Group(models.Model):
    name = models.CharField(max_length=100)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
class Role(models.Model):
    name = models.CharField(max_length=50)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='roles')

    def __str__(self):
        return self.name

class Player(models.Model):
    name = models.CharField(max_length=100)
    birth_date = models.DateField()
    #role = models.CharField(max_length=50)
    role = models.ForeignKey(Role, null=True, blank=True, on_delete=models.SET_NULL)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    

    @property
    def age(self):
        if not self.birth_date:
            return 0
        today = date.today()
        return today.year - self.birth_date.year - (
            (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
        )
    
    def __str__(self):
        return self.name

class GroupJoinRequest(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'In attesa'),
        ('accepted', 'Accettata'),
        ('rejected', 'Rifiutata'),
    ], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Richiesta di adesione al gruppo"
        verbose_name_plural = "Richieste di adesione ai gruppi"
        unique_together = ('user', 'group')

    def __str__(self):
        return f"{self.user.username} → {self.group.name} ({self.status})"
    



