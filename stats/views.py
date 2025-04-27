from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q,  Avg, Count, Sum
from django.shortcuts import render, get_object_or_404, redirect
from matches.models import Match, MatchPerformance, MatchMVPVote, MatchComment, MatchTeamAssignment
from groups.models import Player, Group
from stats.models import PlayerVote, PlayerStats



@login_required
def group_stats_view(request):
    role_filter = request.GET.get("role")
    order_by = request.GET.get("order_by", "presences")
    view_mode = request.GET.get("view", "table")
    group_id = request.GET.get("group_id")

    user_groups = Group.objects.filter(Q(created_by=request.user) | Q(player__user=request.user)).distinct()
    # Recupera le partite giocate del gruppo
    matches = Match.objects.filter(
        group__id=group_id,
        score_team1__isnull=False,
        score_team2__isnull=False,
        is_cancelled=False
    )
    team1_wins = 0
    team2_wins = 0
    draws = 0

    for match in matches:
        if match.score_team1 > match.score_team2:
            team1_wins += 1
        elif match.score_team1 < match.score_team2:
            team2_wins += 1
        else:
            draws += 1
    if not group_id and user_groups.exists():
        group_id = user_groups.first().id

    player_stats = PlayerStats.objects.select_related("player", "player__role") \
        .filter(player__group_id=group_id, player__isnull=False)


    if role_filter:
        player_stats = player_stats.filter(player__role__name=role_filter)

    # Prepara la lista ordinata
    allowed_fields = ["presences", "wins", "goals", "average_vote"]
    if order_by not in allowed_fields:
        order_by = "presences"

    stats = list(player_stats)
    stats.sort(key=lambda x: getattr(x, order_by) or 0, reverse=True)

    roles = Player.objects.filter(group_id=group_id).exclude(role__isnull=True).values_list("role__name", flat=True).distinct()

    return render(request, "stats/group_stats.html", {
        "stats": stats,
        "roles": roles,
        "groups": user_groups,
        "selected_group": int(group_id) if group_id else None,
        "selected_role": role_filter,
        "selected_order_by": order_by,
        "selected_view": view_mode,
        "team1_wins": team1_wins,
        "team2_wins": team2_wins,
        "draws": draws,
    })




@login_required
def review_match_votes(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    squadra1 = MatchTeamAssignment.objects.filter(match=match, team="team1").select_related("player")
    squadra2 = MatchTeamAssignment.objects.filter(match=match, team="team2").select_related("player")
    try:
        current_player = Player.objects.get(user=request.user, group=match.group)
    except Player.DoesNotExist:
        messages.error(request, "Non hai accesso a questa pagina.")
        return redirect("match_list")

    convocated_players = Player.objects.filter(
        matchconvocation__match=match,
        matchconvocation__status='confirmed'
    ).exclude(id=current_player.id)

    existing_votes_qs = PlayerVote.objects.filter(match=match, voter=request.user)
    existing_votes = {vote.voted_player.id: vote.vote for vote in existing_votes_qs}
    user_has_commented = MatchComment.objects.filter(match=match, author=request.user).exists()
    # 🔒 Blocca l'accesso se ha già votato tutti
    if len(existing_votes) == convocated_players.count():
        messages.info(request, "Hai già espresso tutti i tuoi voti.")
        return redirect("match_list")

    if request.method == "POST":
        for player in convocated_players:
            vote_val = request.POST.get(f"vote_{player.id}")
            if vote_val and player.id not in existing_votes:
                PlayerVote.objects.create(
                    match=match,
                    voter=request.user,
                    voted_player=player,
                    vote=int(vote_val)
                )
        # --- Voto MVP ---
        mvp_id = request.POST.get("mvp")
        if mvp_id:
            MatchMVPVote.objects.update_or_create(
                match=match,
                voter=request.user,
                defaults={"voted_player_id": mvp_id}
            )

        # --- Commento post-partita ---
        commento = request.POST.get("commento")
        if commento:
            MatchComment.objects.update_or_create(
                match=match,
                author=request.user,
                defaults={"content": commento}
            )
        update_average_votes(match.group)
        messages.success(request, "Voti registrati e media aggiornata correttamente.")
        return redirect("match_list")

    # 🔁 Voti predefiniti a 3 per i giocatori non ancora votati
    pending_votes = {player.id: 3 for player in convocated_players if player.id not in existing_votes}
    all_votes = {**pending_votes, **existing_votes}
   
    return render(request, "stats/review_match_votes.html", {
        "match": match,
        "squadra1": [x.player for x in squadra1 if x.player != current_player],
        "squadra2": [x.player for x in squadra2 if x.player != current_player],
        "existing_votes": all_votes,
        "user_has_commented": user_has_commented,
    })

# @login_required
# def player_stats_detail(request, player_id):
#     player = get_object_or_404(Player, id=player_id)

#     # Ottieni il gruppo selezionato dalla query string (?group=...)
#     group_id = request.GET.get("group")
#     if not group_id:
#         messages.error(request, "Gruppo non specificato.")
#         return redirect("group_stats")

#     matches = Match.objects.filter(
#         group_id=group_id,
#         is_cancelled=False,
#         score_team1__isnull=False,
#         score_team2__isnull=False,
#     )
#     performances = MatchPerformance.objects.filter(player=player, match__in=matches)
#     votes = PlayerVote.objects.filter(voted_player=player, match__in=matches).select_related("voter")

#     match_data = []
#     for match in matches:
#         goal_entry = performances.filter(match=match).first()
#         player_votes = votes.filter(match=match)
#         match_data.append({
#             "match": match,
#             "goals": goal_entry.goals if goal_entry else 0,
#             "votes": player_votes
#         })

#     return render(request, "stats/player_stats_detail.html", {
#         "player": player,
#         "match_data": match_data,
#     })
@login_required
def player_stats_detail(request, player_id):
    player = get_object_or_404(Player, id=player_id)

    # Ottieni il gruppo selezionato dalla query string (?group=...)
    group_id = request.GET.get("group")
    if not group_id:
        messages.error(request, "Gruppo non specificato.")
        return redirect("group_stats")

    matches = Match.objects.filter(
        group_id=group_id,
        is_cancelled=False,
        score_team1__isnull=False,
        score_team2__isnull=False,
    )

    performances = MatchPerformance.objects.filter(player=player, match__in=matches)
    votes = PlayerVote.objects.filter(voted_player=player, match__in=matches).select_related("voter")
    assignments = MatchTeamAssignment.objects.filter(player=player, match__in=matches).select_related("match")

    match_data = []
    team1_presences = 0
    team2_presences = 0
    team1_goals = 0
    team2_goals = 0

    for match in matches:
        assignment = next((a for a in assignments if a.match_id == match.id), None)
        team = assignment.team if assignment else None
        goal_entry = performances.filter(match=match).first()
        player_votes = votes.filter(match=match)
        goals = goal_entry.goals if goal_entry else 0

        if team == "team1":
            team1_presences += 1
            team1_goals += goals
        elif team == "team2":
            team2_presences += 1
            team2_goals += goals

        match_data.append({
            "match": match,
            "team": team,
            "goals": goals,
            "votes": player_votes
        })

    return render(request, "stats/player_stats_detail.html", {
        "player": player,
        "match_data": match_data,
        "presenze_totali": team1_presences + team2_presences,
        "team1_presenze": team1_presences,
        "team2_presenze": team2_presences,
        "team1_goals": team1_goals,
        "team2_goals": team2_goals,
    })

def update_average_votes(group):
    players = Player.objects.filter(group=group)
    group_matches = Match.objects.filter(group=group)
    for player in players:
        votes = PlayerVote.objects.filter(
            voted_player=player,
            match__in=group_matches
        )
        avg_vote = votes.aggregate(avg=Avg("vote"))["avg"]

        stats, _ = PlayerStats.objects.get_or_create(player=player, group=group)
        stats.average_vote = round(avg_vote, 2) if avg_vote is not None else 0
        stats.save()
