from django.urls import path
from . import views

urlpatterns = [
    path("getMessage/", views.getMessage, name="getMessage"),
]
