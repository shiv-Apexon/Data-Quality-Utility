from django.urls import path

from . import views

urlpatterns = [
    path("connect-db/", views.connect_db, name="connect-db"),
    path("", views.index, name="index"),

]