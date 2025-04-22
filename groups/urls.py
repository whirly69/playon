from django.urls import path
from . import views

urlpatterns = [
    
    path('new/', views.group_create, name='group_create'),
    
]

urlpatterns += [
    path('usergroups/', views.user_groups_view, name='user_groups'),
    path('disponibili/', views.available_groups, name='available_groups'),
    path('<int:group_id>/richiedi/', views.send_join_request, name='send_join_request'),
    path('richieste/manage/', views.manage_requests, name='manage_requests'),
    path('richiesta/<int:request_id>/assign-player/', views.assign_player, name='assign_player'),
    path('richiesta/<int:request_id>/<str:action>/', views.handle_request, name='handle_request'),
    path('associate/<int:group_id>/', views.associate_self_player, name='associate_self_player'),
    path('richieste/', views.pending_requests_view, name='pending_requests'),
    path('richieste/crea_player/<int:request_id>/', views.create_and_assign_player, name='create_and_assign_player'),
]

urlpatterns += [
    path('richiesta/<int:request_id>/select-player/', views.select_player, name='select_player'),
    #path('richiesta/<int:request_id>/assign-player/<int:player_id>/', views.assign_player, name='assign_player'),
    
    path('dashboard/', views.group_dashboard, name='group_dashboard'),
    path('player/<int:player_id>/modifica/', views.player_update, name='player_update'),
    path('groups/<int:group_id>/elimina/', views.group_delete, name='group_delete'),
    path('players/<int:player_id>/delete/', views.player_delete, name='player_delete'),
    path("ruolo/modifica/", views.role_edit_selected, name="role_edit_selected"),
    path("ruolo/elimina/", views.role_delete_selected, name="role_delete_selected"),
]
