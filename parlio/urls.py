from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("annunciator", views.annunciator, name="annunciator"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("question", views.question, name="question"),

    path("fetch", views.fetch, name="fetch"),
    path("onWatchlist/<int:questionId>", views.onWatchlist, name="onWatchlist"),
    path("notifyCheck", views.notifyCheck, name="notifyCheck"),
    path("bookmark/<int:questionId>", views.bookmark, name="bookmark"),
    path("notifyMe/<int:questionId>", views.notifyMe, name="notifyMe"),
    path("isSitting", views.isSitting, name="isSitting")
]