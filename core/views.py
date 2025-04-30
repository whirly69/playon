from django.conf import settings
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Q
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse
from groups.models import Group, GroupJoinRequest, Player
from matches.models import Match
from notifications.models import Notification
from .forms import ContattoForm

@login_required
def contatto_view(request):
    if request.method == 'POST':
        form = ContattoForm(request.POST)
        if form.is_valid():
            tipo = form.cleaned_data['tipo']
            messaggio = form.cleaned_data['messaggio']
            mittente = request.user.get_full_name() or request.user.username

            subject = f"[PlayOn - {tipo.upper()}] da {mittente}"
            body = f"Utente: {mittente} ({request.user.email})\n\n{messaggio}"

            send_mail(subject, body, 'noreply@playonapp.it', ['riohitech@gmail.com'])

            return render(request, 'core/contatto_successo.html')
    else:
        form = ContattoForm()

    return render(request, 'core/contatto.html', {'form': form})



@login_required
def homepage(request):
    user = request.user
    now = timezone.now()

    # Gruppi a cui l'utente non è ancora iscritto né ha richiesto l'iscrizione
    joined_groups = Player.objects.filter(user=user).values_list('group_id', flat=True)
    requested_groups = GroupJoinRequest.objects.filter(user=user).select_related('group')
    available_groups = Group.objects.exclude(id__in=joined_groups) \
                                .exclude(id__in=requested_groups) \
                                .exclude(created_by=request.user)
    unread_count = 0
    if request.user.is_authenticated:
        unread_count = Notification.objects.filter(user=request.user, is_read=False).count()

    if user.role == 'organizer':
        pending_count = GroupJoinRequest.objects.filter(group__created_by=user, status='pending').count()
    else:
        pending_count = 0

    # Gruppi creati dall'utente
    own_groups = Group.objects.filter(created_by=user)

    # Partite future nei gruppi a cui è iscritto
    player_groups = Player.objects.filter(user=user).values_list('group_id', flat=True)
    upcoming_matches = Match.objects.filter(group_id__in=player_groups, date__gte=now.date()).order_by('date', 'time')

    # Richieste di iscrizione ricevute se l’utente è organizzatore
    received_requests = GroupJoinRequest.objects.filter(group__created_by=user)
    # Gruppi in cui l'utente è associato come Player
    user_groups = Group.objects.filter(player__user=user).distinct()    

    # Gruppi in cui l’utente è creatore ma non ancora Player
    pending_association = {
        group.id for group in own_groups
        if not Player.objects.filter(group=group, user=user).exists()
    }
    
    context = {
        'user_groups': user_groups,
        'available_groups': available_groups,
        'own_groups': own_groups,
        'upcoming_matches': upcoming_matches,
        'received_requests': received_requests,
        'pending_requests': requested_groups,
        'pending_association': pending_association,
        'pending_requests_count': pending_count,
        'unread_notifications': unread_count
    }
    return render(request, 'core/homepage.html', context)

def credits_view(request):
    return render(request, "core/credits.html")

def manuale_view(request):
    return render(request, "core/manuale.html")