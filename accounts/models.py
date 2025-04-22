from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ('organizer', 'Organizzatore'),
        ('player', 'Giocatore'),
    ]
    birth_date = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='player')
    player_role = models.CharField(  # Ruolo in campo
        max_length=50,
        blank=True,
        verbose_name="Ruolo in campo",
        help_text="Es. Portiere, Difensore, ecc."
    )