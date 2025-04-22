from django.db import models
from django.conf import settings
from groups.models import Group, Player
from facilities.models import Structure
#from core.models import Facility  # se hai un modello struttura
from django.conf import settings


class Match(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()
    structure = models.ForeignKey(Structure, on_delete=models.SET_NULL, null=True, blank=True)
    players_per_team = models.IntegerField()
    is_public = models.BooleanField(default=False)
    is_cancelled = models.BooleanField(default=False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    score_team1 = models.PositiveSmallIntegerField(null=True, blank=True)
    score_team2 = models.PositiveSmallIntegerField(null=True, blank=True)

    class Meta:
        verbose_name = "Partita"
        verbose_name_plural = "Partite"
        ordering = ['date', 'time']

    def __str__(self):
        return f"Partita del {self.date} ({self.group.name})"

class CallUp(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    confirmed = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Convocazione"
        verbose_name_plural = "Convocazioni"

    def __str__(self):
        return f"{self.player.name} - {self.match.date}"

class MatchConvocation(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=[
        ('invited', 'Convocato'),
        ('confirmed', 'Confermato'),
        ('declined', 'Assente'),
    ], default='invited')

    class Meta:
        verbose_name = "Convocazione Giocatore"
        verbose_name_plural = "Convocazioni Giocatori"
        unique_together = ('match', 'player')

    def __str__(self):
        return f"{self.player.name} - {self.match.date} ({self.status})"
    
class MatchPerformance(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    goals = models.PositiveSmallIntegerField(default=0)
    

    class Meta:
        verbose_name = "Prestazione Giocatore"
        verbose_name_plural = "Prestazioni Giocatori"
        unique_together = ('match', 'player')

    def __str__(self):
        return f"{self.player.name} - {self.match.date}"

class MatchTeamAssignment(models.Model):
    TEAM_CHOICES = [
        ('team1', 'Squadra 1'),
        ('team2', 'Squadra 2'),
    ]
    match = models.ForeignKey('Match', on_delete=models.CASCADE)
    player = models.ForeignKey('groups.Player', on_delete=models.CASCADE)
    team = models.CharField(max_length=10, choices=TEAM_CHOICES)
    vote = models.PositiveSmallIntegerField(default=3)  # 👈 nuovo campo
    
    class Meta:
        verbose_name = "Assegnazione Giocatore a Squadra"
        verbose_name_plural = "Assegnazioni Giocatori a Squadra"
        unique_together = ('match', 'player')

class MatchComment(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Commento Partita"
        verbose_name_plural = "Commenti Partita"
        unique_together = ("match", "author")

class MatchMVPVote(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    voter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    voted_player = models.ForeignKey(Player, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Voto MVP"
        verbose_name_plural = "Voti MVP"
        unique_together = ("match", "voter")
