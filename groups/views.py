
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db.models import Q
from .models import Group, Player, GroupJoinRequest, Role
from .forms import GroupForm, PlayerForm,RoleForm
import logging
logger = logging.getLogger(__name__)




@login_required
def group_list(request):
    groups = Group.objects.filter(created_by=request.user)
    return render(request, 'groups/group_list.html', {'groups': groups})

@login_required
def group_create(request):
    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group.created_by = request.user
            group.save()
            return redirect('group_dashboard')
    else:
        form = GroupForm()
    return render(request, 'groups/group_form.html', {'form': form})

@login_required
def player_add(request, group_id):
    from .models import Group
    group = Group.objects.get(id=group_id)
    if request.method == 'POST':
        form = PlayerForm(request.POST)
        if form.is_valid():
            player = form.save(commit=False)
            player.group = group
            player.save()
            return redirect('group_list')
    else:
        form = PlayerForm()
    return render(request, 'groups/player_form.html', {'form': form, 'group': group})

@login_required
def available_groups(request):
    
    groups = Group.objects.exclude(created_by=request.user)
    requests = GroupJoinRequest.objects.filter(user=request.user)
    requested_ids = requests.values_list('group_id', flat=True)
    pending_association = requests.filter(status='pending').values_list('group_id', flat=True)
    accepted_ids = requests.filter(status='accepted').values_list('group_id', flat=True)
    rejected_ids = requests.filter(status='rejected').values_list('group_id', flat=True)

    return render(request, 'groups/available_groups.html', {
        'groups': groups,
        'requested_ids': requested_ids,
        'pending_association': pending_association,
        'accepted_ids': accepted_ids,
        'rejected_ids': rejected_ids,
    })

# @login_required
# def send_join_request(request, group_id):
#     group = Group.objects.get(id=group_id)
#     already_requested = GroupJoinRequest.objects.filter(user=request.user, group=group).exists()
#     if not already_requested:
#         GroupJoinRequest.objects.create(user=request.user, group=group)
#     return redirect('available_groups')
@login_required
def send_join_request(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    existing_request = GroupJoinRequest.objects.filter(user=request.user, group=group).first()

    if existing_request:
        if existing_request.status == 'rejected':
            existing_request.status = 'pending'
            existing_request.created_at = timezone.now()
            existing_request.save()
    else:
        GroupJoinRequest.objects.create(user=request.user, group=group)

    return redirect('available_groups')


@login_required
def manage_requests(request):
    # Tutti i gruppi creati dall'utente
    groups = Group.objects.filter(created_by=request.user)

    # Tutte le richieste in sospeso
    requests = GroupJoinRequest.objects.filter(group__in=groups, status='pending')

    # Crea un dizionario: { group_id: [players disponibili] }
    players_by_group = {
        group.id: Player.objects.filter(group=group, user__isnull=True)
        for group in groups
    }
    roles_by_group = {
        group.id: Role.objects.filter(group=group)
        for group in groups
    }
    context = {
        'requests': requests,
        'players_by_group': players_by_group,
        'roles_by_group': roles_by_group
    }
    return render(request, 'groups/manage_requests.html', context)

@login_required
def handle_request(request, request_id, action):
    join_request = get_object_or_404(GroupJoinRequest, id=request_id)
    if join_request.group.created_by != request.user:
        return redirect('group_list')
    
    if action == 'accept':
        join_request.status = 'accepted'
        join_request.save()
        # 🔁 Vai alla selezione Player per associare
        return redirect('select_player', request_id=join_request.id)
    elif action == 'reject':
        join_request.status = 'rejected'
        join_request.save()

    return redirect('manage_requests')

@login_required
def select_player(request, request_id):
    join_request = GroupJoinRequest.objects.get(id=request_id)
    group = join_request.group
    players = Player.objects.filter(group=group, user__isnull=True)
    return render(request, 'groups/select_player_modal.html', {
        'join_request': join_request,
        'players': players,
    })

# @login_required
# def assign_player(request, request_id, player_id):
#     player = get_object_or_404(Player, id=player_id, user__isnull=True)

#     # Determina se è una richiesta normale o auto-associazione
#     if request_id == 0:
#         group_id = request.POST.get("group_id")
#         group = get_object_or_404(player.group.__class__, id=group_id)

#         if group.created_by != request.user or player.group != group:
#             messages.error(request, "Non sei autorizzato.")
#             return redirect("user_groups")

#         # Auto-associazione organizzatore
#         player.user = request.user

#     else:
#         join_request = get_object_or_404(GroupJoinRequest, id=request_id)

#         if join_request.group.created_by != request.user or player.group != join_request.group:
#             messages.error(request, "Accesso negato.")
#             return redirect("manage_requests")

#         # Associazione normale (altra richiesta)
#         player.user = join_request.user
#         join_request.status = 'accepted'
#         join_request.save()

#     # Aggiorna dati utente nel profilo Player
#     if player.user.birth_date:
#         player.birth_date = player.user.birth_date

#     if player.user.player_role:
#         try:
#             role_instance = Role.objects.get(name=player.user.player_role)
#             player.role = role_instance
#         except Role.DoesNotExist:
#             pass

#     player.save()

#     # Redirect diverso a seconda del contesto
#     return redirect("user_groups" if request_id == 0 else "manage_requests")

@login_required
def assign_player(request, request_id):
    if request.method != "POST":
        messages.error(request, "Metodo non consentito.")
        return redirect("manage_requests")

    player_id = request.POST.get("player_id")
    if not player_id:
        messages.error(request, "Profilo non selezionato.")
        return redirect("manage_requests")

    player = get_object_or_404(Player, id=player_id, user__isnull=True)

    if request_id == 0:
        # Auto-associazione dell'organizzatore
        group_id = request.POST.get("group_id")
        group = get_object_or_404(player.group.__class__, id=group_id)

        if group.created_by != request.user or player.group != group:
            messages.error(request, "Non sei autorizzato.")
            return redirect("user_groups")

        player.user = request.user
        player.name = f"{request.user.first_name} {request.user.last_name}"
        player.birth_date = request.user.birth_date
        # Non modifichiamo nome o ruolo

    else:
        # Associazione normale tramite richiesta utente
        join_request = get_object_or_404(GroupJoinRequest, id=request_id)

        if join_request.group.created_by != request.user or player.group != join_request.group:
            messages.error(request, "Accesso negato.")
            return redirect("manage_requests")

        player.user = join_request.user
        player.name = f"{player.user.first_name} {player.user.last_name}"
        player.birth_date = player.user.birth_date
        join_request.status = 'accepted'
        join_request.save()

    player.save()

    return redirect("user_groups" if request_id == 0 or str(request_id) == "0" else "manage_requests")


@login_required
def group_manage(request, group_id):
    group = get_object_or_404(Group, id=group_id, created_by=request.user)
    players = Player.objects.filter(group=group)

    if request.method == 'POST':
        form = PlayerForm(request.POST)
        if form.is_valid():
            player = form.save(commit=False)
            player.group = group
            player.save()
            return redirect('group_manage', group_id=group.id)
    else:
        form = PlayerForm()

    return render(request, 'groups/group_manage.html', {
        'group': group,
        'form': form,
        'players': players
    })



@login_required
def group_dashboard(request):
    groups = Group.objects.filter(created_by=request.user).order_by('name')
    # Inizializza variabili per POST    
    form = None
    role_forms = {}
    player_forms = {}
    filtered_players_by_group = {}
    selected_roles_by_group = {}
    group_id = request.POST.get('group_id')

    # Se è un POST (aggiunta giocatore o ruolo)
    if request.method == 'POST':
        form_type = request.POST.get('form_type')

        if form_type == 'role':
            # Aggiunta ruolo
            role_form = RoleForm(request.POST)
            if role_form.is_valid() and group_id:
                role = role_form.save(commit=False)
                role.group_id = group_id
                role.save()
                return redirect('group_dashboard')
        else:
            # Aggiunta giocatore
            form = PlayerForm(request.POST, group_id=group_id)
            if form.is_valid() and group_id:
                player = form.save(commit=False)
                player.group_id = group_id
                player.save()
                return redirect('group_dashboard')
    
    # Se GET o form non valido
    for group in groups:
        role_forms[group.id] = RoleForm()
        for player in group.player_set.all():
            player_forms[player.id] = PlayerForm(instance=player, group_id=group.id)

        # Filtro per ruolo da GET
        selected_role_id = request.GET.get(f'role_filter_{group.id}','')
        if selected_role_id == 'none':
            players = group.player_set.filter(role__isnull=True)
        elif selected_role_id:
            players = group.player_set.filter(role_id=selected_role_id)
        else:
            players = group.player_set.all()

        filtered_players_by_group[group.id] = players
        selected_roles_by_group[group.id] = selected_role_id
        if not form and group.id == int(group_id) if group_id else groups.first().id:
            form = PlayerForm(group_id=group.id)

    context = {
        'groups': groups,
        'form': form,
        'role_forms': role_forms,
        'player_forms': player_forms,
        'filtered_players_by_group': filtered_players_by_group,
        'selected_roles_by_group': selected_roles_by_group,
        'roles_by_group': {
            group.id: group.roles.all() for group in groups
        },
    }
    return render(request, 'groups/group_dashboard.html', context)


@login_required
def player_update(request, player_id):
    player = get_object_or_404(Player, id=player_id)
    if request.method == 'POST':
        form = PlayerForm(request.POST, instance=player)
        if form.is_valid():
            form.save()
    return redirect('group_dashboard')

@login_required
def group_delete(request, group_id):
    group = get_object_or_404(Group, id=group_id, created_by=request.user)
    if request.method == 'POST':
        group.delete()
        messages.success(request, "Gruppo eliminato con successo.")
    return redirect('group_dashboard')

@login_required
def player_delete(request, player_id):
    player = get_object_or_404(Player, id=player_id)

    # Controllo: solo il creatore del gruppo può eliminare
    if request.user != player.group.created_by:
        messages.error(request, "Non hai i permessi per eliminare questo giocatore.")
        return redirect('group_dashboard')

    group = player.group
    user = player.user  # salva prima della cancellazione
    player.delete()
    # Aggiorna la join request se esiste
    if user:
        join_request = GroupJoinRequest.objects.filter(user=user, group=group).first()
        if join_request:
            join_request.status = 'rejected'
            join_request.save()

    messages.success(request, f"Giocatore '{player.name}' eliminato con successo.")
    return redirect('group_dashboard')


@require_POST
@login_required
def role_delete_selected(request):
    role_id = request.POST.get("role_id")
    group_id = request.POST.get("group_id")

    if role_id:
        try:
            role = Role.objects.get(id=role_id, group_id=group_id)
            role.delete()
            messages.success(request, "Ruolo eliminato correttamente.")
        except Role.DoesNotExist:
            messages.error(request, "Ruolo non trovato o non appartiene al gruppo.")
    else:
        messages.error(request, "Nessun ruolo selezionato.")

    return redirect("group_dashboard")

@login_required
def role_edit_selected(request):
    if request.method == "POST":
        role_id = request.POST.get("role_id")
        group_id = request.POST.get("group_id")
        new_name = request.POST.get("role_name")

        if role_id and new_name:
            role = get_object_or_404(Role, id=role_id, group_id=group_id)
            role.name = new_name.strip()
            role.save()
            messages.success(request, "Ruolo modificato con successo.")
        else:
            messages.error(request, "Errore nella modifica del ruolo.")

    return redirect("group_dashboard")

@login_required
def associate_self_player(request, group_id):
    group = get_object_or_404(Group, id=group_id, created_by=request.user)
    # Fittizia join_request creata per riutilizzare il flusso esistente
    join_request, created = GroupJoinRequest.objects.get_or_create(
        user=request.user,
        group=group,
        defaults={'status': 'accepted'}
    )

    return redirect('select_player', request_id=join_request.id)

@login_required
def pending_requests_view(request):
    requests = GroupJoinRequest.objects.filter(user=request.user)
    return render(request, 'groups/pending_requests.html', {'requests': requests})

@login_required
def user_groups_view(request):
    user = request.user

    # Gruppi in cui l'utente è associato come Player (oggetti Group, non solo ID)
    joined_groups = Group.objects.filter(player__user=user).distinct()

    # Gruppi creati da lui
    created_groups = Group.objects.filter(created_by=user)

    # Gruppi dove non è ancora associato come Player
    associated_group_ids = set(joined_groups.values_list("id", flat=True))
    pending_association = {group.id for group in created_groups if group.id not in associated_group_ids}

    # Dizionario: {group_id: [Player liberi]}
    players_by_group = {
        group.id: Player.objects.filter(group=group, user__isnull=True)
        for group in created_groups
    }

    return render(request, 'groups/user_groups.html', {
        'joined_groups': joined_groups,
        'created_groups': created_groups,
        'pending_association': pending_association,
        'players_by_group': players_by_group,
    })

@login_required
def create_and_assign_player(request, request_id):
    join_request = get_object_or_404(GroupJoinRequest, id=request_id)
    if join_request.group.created_by != request.user:
        return redirect('manage_requests')

    if request.method == 'POST':
        role_id = request.POST.get("role_id")
        role = get_object_or_404(Role, id=role_id)

        Player.objects.create(
            user=join_request.user,
            group=join_request.group,
            name=f"{join_request.user.first_name} {join_request.user.last_name}",
            birth_date=join_request.user.birth_date,  # ✅ Presunto campo sul modello User
            role=role
        )

        join_request.status = 'accepted'
        join_request.save()

    return redirect('manage_requests')