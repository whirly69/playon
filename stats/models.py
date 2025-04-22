from django.db import models
from django.conf import settings
from groups.models import Player, Group
from matches.models import Match

class PlayerStats(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    presences = models.PositiveIntegerField(default=0)
    wins = models.PositiveIntegerField(default=0)
    draws = models.PositiveIntegerField(default=0)
    losses = models.PositiveIntegerField(default=0)
    goals = models.PositiveIntegerField(default=0)
    average_vote = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True) 
    top_scorer = models.BooleanField(default=False)
    mvp_count = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name = "Statistiche Giocatore"
        verbose_name_plural = "Statistiche Giocatori"
        unique_together = ("player", "group")

    def __str__(self):
        return f"{self.player.name} - {self.group.name}"

class PlayerVote(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    voter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    voted_player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='received_votes')
    vote = models.PositiveSmallIntegerField()  # da 1 a 5

    class Meta:
        verbose_name = "Voto Giocatore"
        verbose_name_plural = "Voti Giocatori"
        unique_together = ('match', 'voter', 'voted_player')  # Un solo voto per giocatore per partita

    def __str__(self):
        return f"{self.voter.username} → {self.voted_player.name} ({self.vote}) in match {self.match.id}"