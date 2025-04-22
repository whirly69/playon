from django.urls import path
from . import views

urlpatterns = [
    path('new/', views.match_create, name='match_create'),
    path('', views.match_list, name='match_list'),
    path('<int:match_id>/inserisci_risultato/', views.insert_result, name='insert_result'),
    path('<int:match_id>/performance/', views.manage_performance, name='manage_performance'),
    #path('<int:match_id>/toggle/<int:player_id>/', views.toggle_callup, name='toggle_callup'),
    path('<int:match_id>/convocazioni/', views.manage_convocations, name='manage_convocations'),
    path('<int:match_id>/annulla/', views.cancel_match, name='cancel_match'),
    path('<int:match_id>/riattiva/', views.reactivate_match, name='reactivate_match'),
    path('<int:match_id>/squadre/', views.manage_teams, name='manage_teams'),
    #path('<int:match_id>/genera/', views.generate_auto_teams, name='generate_auto_teams'),
    path('coerenza/', views.foglio_coerenza_view, name='foglio_coerenza'),
    path('api/match/<int:match_id>/players/', views.get_match_players, name='get_match_players'),
    path('<int:match_id>/statistiche/', views.match_stats_view, name='match_stats'),
    path('<int:match_id>/reply/<str:response>/', views.respond_to_convocation, name='respond_to_convocation'),
    path('<int:match_id>/export-pdf/', views.export_teams_pdf, name='export_teams_pdf'),
    path('<int:match_id>/commenti/', views.match_comments, name='match_comments'),
    path("<int:match_id>/salva_squadre_sessione/", views.salva_squadre_in_sessione, name="salva_squadre_sessione"),

]
