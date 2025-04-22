from django.core.management.base import BaseCommand
from groups.models import Group, Role, Player

class Command(BaseCommand):
    help = 'Crea ruoli per ogni gruppo e li assegna ai giocatori'

    def handle(self, *args, **options):
        for group in Group.objects.all():
            role_map = {}
            for role_name in Player.objects.filter(group=group).values_list('role', flat=True).distinct():
                if role_name:
                    role_obj, created = Role.objects.get_or_create(name=role_name, group=group)
                    role_map[role_name] = role_obj
                    self.stdout.write(f"Creato ruolo '{role_name}' per gruppo '{group.name}'")

            # Associa ogni giocatore al Role (temporaneamente in un campo extra)
            for player in Player.objects.filter(group=group):
                role_obj = role_map.get(player.role)
                if role_obj:
                    player._new_role = role_obj  # solo memoria
                    player.save()