from datetime import datetime
from django.shortcuts import render, reverse
from django.contrib.auth.decorators import login_required
from groups.models import Player
from .models import Notification
from matches.models import  MatchConvocation
from datetime import datetime, timedelta
from django.utils import timezone

@login_required
def notification_list(request):
    notifications = Notification.objects.filter(user=request.user).order_by("-created_at")

    match_times = {}
    now = timezone.now()

    for n in notifications:
        if n.match:
            match_dt = timezone.make_aware(datetime.combine(n.match.date, n.match.time))
            if match_dt - now > timedelta(hours=24):
                match_times[n.id] = {
                    "interagibile": True,
                    "disdici_fino": (match_dt - timedelta(hours=24)).strftime('%d/%m/%Y %H:%M')
                }
            else:
                match_times[n.id] = {
                    "interagibile": False,
                    "disdici_fino": (match_dt - timedelta(hours=24)).strftime('%d/%m/%Y %H:%M')
                }
        else:
            match_times[n.id] = None

    return render(request, "notifications/notification_list.html", {
        "notifications": notifications,
        "match_times": match_times
    })

def create_or_update_notification(user, match, message, link):
    notif, created = Notification.objects.get_or_create(
        user=user,
        match=match,
        defaults={"message": message, "link": link}
    )
    if not created:
        notif.message = message
        notif.link = link
        notif.is_read = False
        notif.save()



def notify_manual_convocations(match, selected_player_ids):
    players = Player.objects.filter(id__in=selected_player_ids, user__isnull=False)

    for player in players:
        convocation = MatchConvocation.objects.filter(match=match, player=player).first()
        if convocation and convocation.status == 'confirmed':
            create_or_update_notification(
                user=player.user,
                match=match,
                message=f"Sei stato confermato tra i convocati per la partita del {match.date.strftime('%d/%m/%Y')} alle {match.time.strftime('%H:%M')}.",
                link=reverse('respond_to_convocation', args=[match.id, 'disdici'])
            )
