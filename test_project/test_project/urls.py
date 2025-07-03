from django.contrib import admin
from django.shortcuts import redirect
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    # Redirect root to the login page
    path("", lambda request: redirect("login/", permanent=False)),
    # Include our auth_app urls
    path("", include("google_auth_app.urls")),
    # Include social_django urls
]
