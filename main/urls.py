from django.urls import path

from . import views

app_name = "main"

urlpatterns = [
    path("", views.home, name="home"),
    path("home2/", views.home2, name="home2"),
    path("scoring/<path:list_data>/", views.scoring, name="scoring"),
    path("scoring2/", views.scoring2, name="scoring2"),
]
