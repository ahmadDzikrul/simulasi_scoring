from django.urls import path

from . import views

app_name = "main"

urlpatterns = [
    path("", views.home, name="home"),
    path("home2/", views.home2, name="home2"),
    path("scoring/", views.scoring, name="scoring"),
]
