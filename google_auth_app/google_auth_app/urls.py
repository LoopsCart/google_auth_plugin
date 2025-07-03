from django.urls import include, path

from . import views
from .views import GoogleCredentialAPIView

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("home/", views.home_view, name="home"),
    path("logout/", views.logout_view, name="logout"),
    #
    path("", include("social_django.urls", namespace="social")),
    path("api/google-credentials/", GoogleCredentialAPIView.as_view(), name="google-credentials"),
    path("google-login/", views.google_login_view, name="google-login"),
]
