from django.urls import path
from . import views

urlpatterns = [
    path('strutture/', views.structure_dashboard, name='structure_dashboard'),
    path('strutture/<int:structure_id>/modifica/', views.structure_update, name='structure_update'),
    path('strutture/<int:structure_id>/elimina/', views.structure_delete, name='structure_delete'),
]