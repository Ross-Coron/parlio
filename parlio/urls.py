from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("annunciator", views.annunciator, name="annunciator"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register")
]