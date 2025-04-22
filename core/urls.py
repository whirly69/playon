from django.urls import path
from .views import homepage, credits_view, manuale_view, contatto_view

urlpatterns = [
    path('', homepage, name='homepage'),
    path("credits/", credits_view, name="credits"),
    path("manuale/", manuale_view, name="manuale"),
    path("contatto/", contatto_view, name="contatto"),
]
