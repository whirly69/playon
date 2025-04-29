from django.conf import settings
from django.contrib import messages
from django.templatetags.static import static
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, JsonResponse
from django.db.models import Count, Q, Prefetch
from django.shortcuts import render, redirect,get_object_or_404
from django.urls import reverse
from django.views.decorators.http import require_http_methods, require_GET, require_POST
from django.utils import timezone
from django.http import HttpResponse, HttpResponseForbidden
from django.template.loader import render_to_string
from weasyprint import HTML
from datetime import datetime, timedelta
from groups.models import Group,Player
from .forms import MatchForm
from .models import Match, MatchConvocation, MatchPerformance, MatchTeamAssignment, MatchMVPVote, MatchComment
from stats.models import PlayerStats
from notifications.views import create_or_update_notification
from collections import  Counter, defaultdict
from statistics import mean
from datetime import date,timedelta
import markdown
import json
import os



ROLE_ORDER = [
    "portiere", "terzino", "esterno basso", "terzino destro", "terzino sinistro",
    "difensore", "difensore esterno", "difensore centrale",
    "centrocampista", "esterno alto", "ala",
    "attaccante esterno", "attaccante"
]

def foglio_coerenza_view(request):
    file_path = os.path.join(settings.BASE_DIR, 'static','docs', 'foglio_coerenza.md')
    if not os.path.exists(file_path):
        return render(request, 'matches/md_page.html', {'content': '<p><strong>File coerenza.md non trovato.</strong></p>'})
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()
    html_content = markdown.markdown(text)
    return render(request, 'matches/foglio_coerenza.html', {'content': html_content})

def ruolo_priority(ruolo):
    r = (ruolo or '').lower()
    return ROLE_ORDER.index(r) if r in ROLE_ORDER else len(ROLE_ORDER)

def role_sort_key(player):
    role = player.role.name.lower() if player.role else ""
    for i, keyword in enumerate(ROLE_ORDER):
        if keyword in role:
            return i
    return 99

def get_team_summary(assignments, players, team_name, voti):
    voti = {int(k): v for k, v in voti.items()}
    team_players = [p for p in players if assignments.get(p.id) == team_name]
    count = len(team_players)
    
    # Usa solo i voti effettivamente presenti
    vote_list = [voti[p.id] for p in team_players if p.id in voti]
    total_score = sum(vote_list)

    # Età media
    avg_age = round(sum(p.age for p in team_players if p.age) / count, 1) if count else '-'

    # Conta i ruoli
    role_count = {}
    for p in team_players:
        if p.role:
            role_name = p.role.name
            role_count[role_name] = role_count.get(role_name, 0) + 1

    # Log per debug
    print(f"🧮 Resoconto {team_name} -> {vote_list}")

    return {
        'count': count,
        'total_score': total_score,
        'avg_age': avg_age,
        'role_count': role_count
    }

@login_required
def match_create(request):
    if request.method == 'POST':
        form = MatchForm(request.POST)
        if form.is_valid():
            match = form.save(commit=False)
            match.created_by = request.user
            match.save()

            # Invita tutti i Player associati al gruppo
            players = Player.objects.filter(group=match.group, user__isnull=False)
            MatchConvocation.objects.bulk_create([
                MatchConvocation(match=match, player=p, status='invited') for p in players
            ])

            for player in players:
                create_or_update_notification(
                    user=player.user,
                    match=match,
                    message=f"Sei stato convocato per la partita del {match.date.strftime('%d/%m/%Y')} alle {match.time.strftime('%H:%M')}",
                    link=reverse('respond_to_convocation', args=[match.id, 'none'])
                )
            return redirect('manage_convocations', match_id=match.id)
    else:
        form = MatchForm()
        form.fields['group'].queryset = request.user.group_set.all()
    return render(request, 'matches/match_form.html', {'form': form})



# @login_required
# def match_list(request):
#     filter_option = request.GET.get('filter', 'all')
#     user_groups = Group.objects.filter(Q(player__user=request.user) | Q(created_by=request.user)).distinct()
#     matches = Match.objects.filter(
#         Q(group__in=user_groups) | Q(is_public=True)
#     ).distinct().order_by('-date', '-time')
    
    
#     if filter_option == 'future':
#         matches = matches.filter(date__gte=date.today())
#     elif filter_option == 'my':
#         matches = matches.filter(created_by=request.user)

#     match_has_teams = {
#         match.id: MatchTeamAssignment.objects.filter(match=match).exists()
#         for match in matches
#     }
    
#     # ✅ Calcola i marcatori per ciascuna squadra
#     match_scorers_map = {}
#     for match in matches:
#         team1_ids = MatchTeamAssignment.objects.filter(match=match, team="team1").values_list("player_id", flat=True)
#         team2_ids = MatchTeamAssignment.objects.filter(match=match, team="team2").values_list("player_id", flat=True)

#         performances = MatchPerformance.objects.filter(match=match).select_related("player")
#         scorers_team1 = [p for p in performances if p.player.id in team1_ids]
#         scorers_team2 = [p for p in performances if p.player.id in team2_ids]

#         match_scorers_map[match.id] = {
#             "team1": scorers_team1,
#             "team2": scorers_team2,
#         }

#     match_mvp_map = {}
#     for match in matches:
#         mvp_votes = MatchMVPVote.objects.filter(match=match)
#         if mvp_votes.exists():
#             top_voted = (
#                 mvp_votes.values('voted_player')
#                 .annotate(count=Count('id'))
#                 .order_by('-count')
#                 .first()
#             )
#             mvp_player = Player.objects.get(id=top_voted['voted_player'])
#             match_mvp_map[match.id] = {
#                 "name": mvp_player.name,
#                 "votes": top_voted['count'],
#             }

#     # ✅ Calcola la presenza di commenti per ogni match (spostato fuori dal blocco MVP)
#     match_has_comments = {
#         match.id: MatchComment.objects.filter(match=match).exists()
#         for match in matches
#     }

#     return render(request, 'matches/match_list.html', {
#         'matches': matches,
#         'match_has_teams': match_has_teams,
#         'filter': filter_option,
#         'match_scorers_map': match_scorers_map,
#         'match_mvp_map': match_mvp_map,
#         'match_has_comments': match_has_comments,
#     })
@login_required
def match_list(request):
    # Recupera i gruppi dell'utente
    user_groups = Group.objects.filter(
        Q(player__user=request.user) | Q(created_by=request.user)
    ).distinct()

    # Precarica matches
    matches = Match.objects.filter(
        Q(group__in=user_groups) | Q(is_public=True)
    ).select_related('structure', 'group', 'created_by') \
    .prefetch_related(
        'matchteamassignment_set',
        'matchperformance_set__player',
        'matchmvpvote_set',
        'matchcomment_set',
    ).distinct().order_by('-date', '-time')

    # ➡️ Ora filtra future/my
    filter_option = request.GET.get('filter', 'all')

    if filter_option == 'future':
        matches = matches.filter(date__gte=date.today())
    elif filter_option == 'my':
        matches = matches.filter(created_by=request.user)

    # ✅ Solo adesso costruiamo TUTTI i dizionari sui match filtrati
    today = date.today()

    match_has_teams = {}
    match_scorers_map = {}
    match_mvp_map = {}
    match_has_comments = {}
    match_votation_expired = {}
    match_votation_days_left = {}

    for match in matches:
        match_has_teams[match.id] = match.matchteamassignment_set.exists()

        team1_players = [a.player.id for a in match.matchteamassignment_set.all() if a.team == "team1"]
        team2_players = [a.player.id for a in match.matchteamassignment_set.all() if a.team == "team2"]

        scorers_team1 = [p for p in match.matchperformance_set.all() if p.player.id in team1_players]
        scorers_team2 = [p for p in match.matchperformance_set.all() if p.player.id in team2_players]

        match_scorers_map[match.id] = {
            "team1": scorers_team1,
            "team2": scorers_team2,
        }

        if match.matchmvpvote_set.exists():
            top_voted = (
                match.matchmvpvote_set.values('voted_player')
                .annotate(count=Count('id'))
                .order_by('-count')
                .first()
            )
            if top_voted:
                mvp_player = Player.objects.get(id=top_voted['voted_player'])
                match_mvp_map[match.id] = {
                    "name": mvp_player.name,
                    "votes": top_voted['count'],
                }

        match_has_comments[match.id] = match.matchcomment_set.exists()

        if match.score_team1 is not None and match.score_team2 is not None:
            votation_deadline = match.date + timedelta(days=4)
            if today > votation_deadline:
                match_votation_expired[match.id] = True
                match_votation_days_left[match.id] = 0
            else:
                match_votation_expired[match.id] = False
                match_votation_days_left[match.id] = (votation_deadline - today).days
        else:
            match_votation_expired[match.id] = False
            match_votation_days_left[match.id] = None

    return render(request, 'matches/match_list.html', {
        'matches': matches,
        'match_has_teams': match_has_teams,
        'filter': filter_option,
        'match_scorers_map': match_scorers_map,
        'match_mvp_map': match_mvp_map,
        'match_has_comments': match_has_comments,
        'match_votation_expired': match_votation_expired,
        'match_votation_days_left': match_votation_days_left,
    })

@login_required
def manage_convocations(request, match_id):
    match = get_object_or_404(Match, id=match_id, created_by=request.user)
    players = Player.objects.filter(group=match.group).order_by('name')
    now = timezone.now()
    match_dt = timezone.make_aware(datetime.combine(match.date, match.time))
    time_left = match_dt - now

    if request.method == 'POST':
        selected_ids = set(map(int, request.POST.getlist('convoked_players')))
        max_players = match.players_per_team * 2

        if len(selected_ids) > max_players:
            messages.error(request, f"Puoi convocare al massimo {max_players} giocatori.")
        else:
            for player in players:
                conv, created = MatchConvocation.objects.get_or_create(match=match, player=player)

                if player.id in selected_ids:
                    if conv.status != 'confirmed':
                        conv.status = 'confirmed'
                        conv.save()

                        if player.user:
                            create_or_update_notification(
                                user=player.user,
                                match=match,
                                message=f"Sei stato inserito tra i convocati per la partita del {match.date.strftime('%d/%m/%Y')} alle {match.time.strftime('%H:%M')}.",
                                link=reverse('respond_to_convocation', args=[match.id, 'disdici']) if time_left >= timedelta(hours=24) else ""
                            )
                else:
                    # if conv.status in ['invited', 'confirmed']:
                    #     conv.delete()
                    if conv.status == 'confirmed':
                        conv.status = 'invited'
                        conv.save()

            messages.success(request, "Convocazioni aggiornate con successo.")
            return redirect('match_list')

    convocations = MatchConvocation.objects.filter(match=match).select_related('player')
    convocated_ids = [c.player.id for c in convocations]
    convocations_status = {c.player.id: c.status for c in convocations}

    declined_after_accept = []
    riproposti = []

    for player in players:
        try:
            conv = MatchConvocation.objects.get(match=match, player=player)
            if conv.status == 'declined':
                if time_left < timedelta(hours=24):
                    declined_after_accept.append(player.id)
                elif MatchConvocation.objects.filter(match=match, player=player, status='confirmed').exists():
                    riproposti.append(player.id)
        except MatchConvocation.DoesNotExist:
            continue

    return render(request, "matches/manage_convocations.html", {
        "match": match,
        "players": players,
        "convocated_ids": convocated_ids,
        "convocations_status": convocations_status,
        "declined_after_accept": declined_after_accept,
        "riproposti": riproposti,
    })


@login_required
def respond_to_convocation(request, match_id, response):
    match = get_object_or_404(Match, id=match_id)
    try:
        player = Player.objects.get(user=request.user, group=match.group)
    except Player.DoesNotExist:
        messages.error(request, "Non sei un giocatore convocabile per questo gruppo.")
        return redirect('match_list')

    conv, _ = MatchConvocation.objects.get_or_create(match=match, player=player)

    now = timezone.now()
    match_dt = timezone.make_aware(datetime.combine(match.date, match.time))
    time_left = match_dt - now

    max_players = match.players_per_team * 2
    confirmed_count = MatchConvocation.objects.filter(match=match, status='confirmed').count()

    if response == 'accept':
        if confirmed_count >= max_players:
            conv.status = 'invited'
            conv.save()
            create_or_update_notification(
                user=request.user,
                match=match,
                message=f"Sei in sovrannumero per la partita del {match.date.strftime('%d/%m/%Y')} alle {match.time.strftime('%H:%M')}. Potresti essere ripescato in caso di rinunce.",
                link=reverse('respond_to_convocation', args=[match.id, 'disdici']) if time_left >= timedelta(hours=24) else ""
            )
            messages.warning(request, "Convocazioni piene. Sei stato messo in sovrannumero.")
        else:
            if conv.status == 'declined' and time_left >= timedelta(hours=24):
                conv.status = 'invited'
                conv.save()
                messages.info(request, "Hai riproposto la tua candidatura. L'organizzatore deciderà se reinserirti.")
            else:
                conv.status = 'confirmed'
                conv.save()
                messages.success(request, f"Hai confermato la tua presenza per la partita del {match.date.strftime('%d/%m/%Y')} alle {match.time.strftime('%H:%M')}.")

            create_or_update_notification(
                user=request.user,
                match=match,
                message=f"Hai confermato la tua presenza per la partita del {match.date.strftime('%d/%m/%Y')} alle {match.time.strftime('%H:%M')}. Puoi disdire entro 24h prima dell'inizio.",
                link=reverse('respond_to_convocation', args=[match.id, 'disdici']) if time_left >= timedelta(hours=24) else ""
            )

    elif response == 'decline':
        conv.status = 'declined'
        conv.save()

        create_or_update_notification(
            user=request.user,
            match=match,
            message=f"Hai rifiutato la convocazione per la partita del {match.date.strftime('%d/%m/%Y')} alle {match.time.strftime('%H:%M')}.",
            link=f"/matches/{match.id}/reply/riproponi/" if time_left >= timedelta(hours=24) else ""
        )

        messages.warning(request, "Hai rifiutato la convocazione.")

    elif response == 'disdici':
        if time_left >= timedelta(hours=24):
            conv.status = 'declined'
            conv.save()

            create_or_update_notification(
                user=request.user,
                match=match,
                message=f"Hai disdetto la convocazione per la partita del {match.date.strftime('%d/%m/%Y')} alle {match.time.strftime('%H:%M')}. Puoi riproporti entro il limite previsto.",
                link=f"/matches/{match.id}/reply/riproponi/"
            )

            messages.info(request, f"Hai disdetto per la partita del {match.date.strftime('%d/%m/%Y')} alle {match.time.strftime('%H:%M')}. Ora puoi riproporti.")
        else:
            messages.error(request, "Non puoi disdire a meno di 24h dalla partita.")
    elif response == 'riproponi':
        if time_left >= timedelta(hours=24):
            conv.status = 'invited'
            conv.save()
            confirmed_count = MatchConvocation.objects.filter(match=match, status='confirmed').count()
            max_players = match.players_per_team * 2

            if confirmed_count >= max_players:
                create_or_update_notification(
                    user=request.user,
                    match=match,
                    message=f"Hai riproposto la tua candidatura per la partita del {match.date.strftime('%d/%m/%Y')} alle {match.time.strftime('%H:%M')}. L'organizzatore valuterà se inserirti.",
                    link=reverse('respond_to_convocation', args=[match.id, 'disdici'])  # ✅ link coerente
                )
                messages.warning(request, f"Convocazioni piene per la partita del {match.date.strftime('%d/%m/%Y')} alle {match.time.strftime('%H:%M')}. Sei stato messo in sovrannumero.")
            else:
                create_or_update_notification(
                    user=request.user,
                    match=match,
                    message=f"Hai riproposto la tua candidatura per la partita del {match.date.strftime('%d/%m/%Y')} alle {match.time.strftime('%H:%M')}. L'organizzatore valuterà se inserirti.",
                    link=reverse('respond_to_convocation', args=[match.id, 'disdici'])
                )
                messages.success(request, "Ti sei riproposto con successo.")
        else:
            messages.warning(request, "Non puoi riproporti a meno di 24h dalla partita.")


    return redirect('match_list')




@login_required
@require_http_methods(["POST"])
def insert_result(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    if request.user != match.created_by:
        return HttpResponseForbidden("Non sei autorizzato")

    try:
        match.score_team1 = int(request.POST.get("score_team1", 0))
        match.score_team2 = int(request.POST.get("score_team2", 0))
        match.save()
    except:
        messages.error(request, "Errore nei punteggi.")
        return redirect("match_list")

    # Conteggio goal per giocatore (marcatori da entrambi i campi)
    marcatori = request.POST.getlist("marcatore_team1[]") + request.POST.getlist("marcatore_team2[]")
    goal_counts = defaultdict(int)
    for pid in marcatori:
        goal_counts[int(pid)] += 1

    # Pulisce vecchi dati e salva solo chi ha segnato
    MatchPerformance.objects.filter(match=match).delete()
    for pid, num_goals in goal_counts.items():
        MatchPerformance.objects.create(
            match=match,
            player_id=pid,
            goals=num_goals
        )

    # 🔁 Aggiorna statistiche globali
    update_player_stats_from_match(match)

    messages.success(request, "Risultato, marcatori e statistiche aggiornati con successo.")
    return redirect("match_list")

@login_required
def manage_performance(request, match_id):
    match = get_object_or_404(Match, id=match_id, created_by=request.user)

    convocated_players = Player.objects.filter(
        matchconvocation__match=match
    ).distinct()

    if request.method == 'POST':
        for player in convocated_players:
            prefix = f"player_{player.id}"
            data = {
                'present': request.POST.get(f'{prefix}_present') == 'on',
                'goals': request.POST.get(f'{prefix}_goals', 0),
                'vote': request.POST.get(f'{prefix}_vote', None),
            }
            obj, created = MatchPerformance.objects.get_or_create(match=match, player=player)
            obj.present = data['present']
            obj.goals = data['goals']
            obj.vote = data['vote'] if data['vote'] != '' else None
            obj.save()
        return redirect('match_list')

    # Precompila i dati già esistenti
    performances = {
        perf.player_id: perf for perf in MatchPerformance.objects.filter(match=match)
    }

    return render(request, 'matches/manage_performance.html', {
        'match': match,
        'players': convocated_players,
        'performances': performances,
    })

@login_required
def cancel_match(request, match_id):
    match = get_object_or_404(Match, id=match_id, created_by=request.user)
    match.is_cancelled = True
    match.save()
    return redirect('match_list')

@login_required
def reactivate_match(request, match_id):
    match = get_object_or_404(Match, id=match_id, created_by=request.user)
    if match.is_cancelled:
        match.is_cancelled = False
        match.save()
    return redirect('match_list')

@login_required
@require_http_methods(["GET", "POST"])
def manage_teams(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    if not (
        match.created_by == request.user or 
        MatchConvocation.objects.filter(match=match, player__user=request.user, status='confirmed').exists()
    ):
        return HttpResponseForbidden("Non hai i permessi per visualizzare questa pagina.")
    can_save = match.created_by == request.user
    # ✅ Solo giocatori con convocazione confermata
    convocations = MatchConvocation.objects.filter(match=match, status='confirmed').select_related('player')
    convocated_players = [c.player for c in convocations]

    # Assegnazioni precedenti
    assignments = MatchTeamAssignment.objects.filter(match=match)
    player_assignments = {a.player_id: a.team for a in assignments}

    # Voti
    votes = request.session.get(f"voti_match_{match_id}", {})

    if request.method == "POST":
        if request.user != match.created_by:
            return HttpResponseForbidden("Solo l'organizzatore può salvare.")
        else:
            new_assignments = {}
            for key, value in request.POST.items():
                if key.startswith("assignment_"):
                    try:
                        pid = int(key.split("_")[1])
                        if any(p.id == pid for p in convocated_players):
                            new_assignments[pid] = value
                    except:
                        pass

            MatchTeamAssignment.objects.filter(match=match).delete()
            for pid, team in new_assignments.items():
                if team in ["team1", "team2"]:
                    MatchTeamAssignment.objects.create(match=match, player_id=pid, team=team)

            messages.success(request, "Squadre salvate correttamente.")
            return redirect("manage_teams", match_id=match_id)

    # Dati per JS
    player_data = [
        {
            "id": p.id,
            "name": p.name,
            "age": p.age,
            "role": p.role.name if p.role else "",
            "team": player_assignments.get(p.id, "none"),
        }
        for p in convocated_players
    ]

    mode = request.GET.get("mode", "manual")

    return render(request, "matches/manage_teams.html", {
        "match": match,
        "mode": mode,
        "player_data": json.dumps(player_data),
        "saved_votes": json.dumps(votes),
        "can_save": can_save,
    })


@login_required
@require_GET
def get_match_players(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    if request.user != match.created_by:
        return JsonResponse({"error": "Non autorizzato"}, status=403)

    assignments = MatchTeamAssignment.objects.filter(match=match)
    players_by_team = {"team1": [], "team2": []}
    for a in assignments:
        if a.team in ["team1", "team2"]:
            players_by_team[a.team].append({"id": a.player.id, "name": a.player.name})

    return JsonResponse(players_by_team)




def update_player_stats_from_match(match):
    team1_players = MatchTeamAssignment.objects.filter(match=match, team="team1").select_related("player")
    team2_players = MatchTeamAssignment.objects.filter(match=match, team="team2").select_related("player")

    score1 = match.score_team1
    score2 = match.score_team2

    all_players = list(team1_players) + list(team2_players)
    for assignment in all_players:
        player = assignment.player
        stats, _ = PlayerStats.objects.get_or_create(player=player, group=match.group)

        # Presenza
        stats.presences += 1

        # Risultato
        if score1 == score2:
            stats.draws += 1
        elif (assignment.team == "team1" and score1 > score2) or (assignment.team == "team2" and score2 > score1):
            stats.wins += 1
        else:
            stats.losses += 1

        # Goal (presi da MatchPerformance)
        goal_entry = MatchPerformance.objects.filter(match=match, player=player).first()
        if goal_entry:
            stats.goals += goal_entry.goals

        stats.save()





def match_stats_view(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    assignments = MatchTeamAssignment.objects.filter(match=match).select_related('player')
    performances = MatchPerformance.objects.filter(match=match)

    player_stats = []
    for assign in assignments:
        perf = performances.filter(player=assign.player).first()
        player_stats.append({
            'player': assign.player,
            'team': assign.team,
            'goals': perf.goals if perf else 0,
            'vote': perf.vote if perf else None,
        })

    return render(request, 'matches/match_stats.html', {
        'match': match,
        'player_stats': player_stats
    })


@login_required
@require_GET
def export_teams_pdf(request, match_id):
    match = get_object_or_404(Match, id=match_id)

    # Accesso consentito solo a organizzatore o giocatori convocati confermati
    if not (
        request.user == match.created_by or
        MatchConvocation.objects.filter(match=match, player__user=request.user, status='confirmed').exists()
    ):
        return HttpResponseForbidden("Accesso negato")

    # Voti personalizzati salvati in sessione
    votes = request.session.get(f"voti_match_{match_id}", {})

    # Proposta di formazioni personalizzate (lavagna) salvate in sessione
    team1_ids = request.session.get(f"squadra1_match_{match_id}")
    team2_ids = request.session.get(f"squadra2_match_{match_id}")

    if team1_ids and team2_ids:
        team1 = list(Player.objects.filter(id__in=team1_ids).select_related('role'))
        team2 = list(Player.objects.filter(id__in=team2_ids).select_related('role'))
    else:
        # Fallback: tutti i convocati in una sola lista (se nulla in sessione)
        convocati = Player.objects.filter(
            matchconvocation__match=match,
            matchconvocation__status="confirmed"
        ).select_related("role")
        team1 = list(convocati)
        team2 = []

    # Applica voto aggiornato dalla sessione
    for p in team1 + team2:
        p.vote = votes.get(str(p.id), 3)

    # Ordina le squadre per ruolo
    team1.sort(key=role_sort_key)
    team2.sort(key=role_sort_key)

    def summarize(team):
        role_count = Counter()
        total_score = 0
        total_age = 0
        valid_ages = 0
        for p in team:
            if p.role:
                role_count[p.role.name] += 1
            total_score += p.vote
            if p.age:
                total_age += p.age
                valid_ages += 1
        return {
            "count": len(team),
            "role_count": dict(role_count),
            "total_score": total_score,
            "avg_age": round(total_age / valid_ages, 1) if valid_ages else "-"
        }

    summary1 = summarize(team1)
    summary2 = summarize(team2)

    html_string = render_to_string("matches/teams_pdf.html", {
        "match": match,
        "team1": team1,
        "team2": team2,
        "summary1": summary1,
        "summary2": summary2,
        "generated_by": request.user.get_full_name() or request.user.username
    })

    base_url = os.path.join(settings.BASE_DIR, 'static')
    pdf_file = HTML(string=html_string, base_url=base_url).write_pdf()
    response = HttpResponse(pdf_file, content_type="application/pdf")
    response["Content-Disposition"] = f'filename="formazioni_{match.id}.pdf"'
    return response

@login_required
@require_POST
def salva_squadre_in_sessione(request, match_id):
    data = json.loads(request.body)
    request.session[f"squadra1_match_{match_id}"] = data.get("team1", [])
    request.session[f"squadra2_match_{match_id}"] = data.get("team2", [])
    request.session[f"voti_match_{match_id}"] = data.get("votes", {})
    return JsonResponse({"ok": True})

# @login_required
# @require_GET
# def export_teams_pdf(request, match_id):
#     match = get_object_or_404(Match, id=match_id)
#     if not (request.user == match.created_by or MatchConvocation.objects.filter(match=match, player__user=request.user, status='confirmed').exists()):
#         return HttpResponseForbidden("Accesso negato")

#     assignments = MatchTeamAssignment.objects.filter(match=match).select_related('player__role')
#     votes = request.session.get(f"voti_match_{match_id}", {})

#     team1 = []
#     team2 = []

#     for a in assignments:
#         a.player.vote = votes.get(str(a.player.id), 3)  # default voto 3
#         if a.team == "team1":
#             team1.append(a.player)
#         elif a.team == "team2":
#             team2.append(a.player)

#     def summarize(team):
#         role_count = Counter()
#         total_score = 0
#         for p in team:
#             if p.role:
#                 role_count[p.role.name] += 1
#             total_score += p.vote
#         return {
#             "count": len(team),
#             "role_count": dict(role_count),
#             "total_score": total_score
#         }

#     summary1 = summarize(team1)
#     summary2 = summarize(team2)

#     html_string = render_to_string("matches/teams_pdf.html", {
#         "match": match,
#         "team1": team1,
#         "team2": team2,
#         "summary1": summary1,
#         "summary2": summary2,
#         "generated_by": request.user.get_full_name() or request.user.username
#     })

#     base_url = os.path.join(settings.BASE_DIR, 'static')
#     pdf_file = HTML(string=html_string, base_url=base_url).write_pdf()
#     response = HttpResponse(pdf_file, content_type="application/pdf")
#     response["Content-Disposition"] = f'filename="formazioni_{match.id}.pdf"'
#     return response

@login_required
def match_comments(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    comments = MatchComment.objects.filter(match=match).select_related('author').order_by('-created_at')
    return render(request, "matches/match_comments.html", {
        "match": match,
        "comments": comments
    })