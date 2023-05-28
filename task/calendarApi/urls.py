from django.urls import path
from  . import views

urlpatterns = [
    path('rest/v1/calendar/init/', views.GoogleCalendarInitView),
    path('rest/v1/calendar/redirect/', views.GoogleCalendarRedirectView),
]