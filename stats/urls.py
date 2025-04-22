from django.urls import path
from . import views

urlpatterns = [
    path('generali/', views.group_stats_view, name='group_stats'),
    path("player/<int:player_id>/stats/", views.player_stats_detail, name="player_stats_detail"),

    path('<int:match_id>/review/', views.review_match_votes, name='review_match_votes'),
]