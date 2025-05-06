from django.urls import path
from . import views

urlpatterns = [
    path('', views.notification_list, name='notification_list'),
    path('viewed/<int:pk>/', views.mark_notification_read, name='mark_notification_read'),

]
