from django.contrib.auth import logout
from django.http import JsonResponse
from django.shortcuts import redirect, render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import GoogleCredential
from .serializers import GoogleCredentialSerializer


def login_view(request):
    """
    Renders the login page.
    """
    return render(request, "google_auth_app/login.html")


def wsgi_meta_view(request):
    meta = dict(request.META)
    filtered_meta = {k: str(v) for k, v in meta.items()}  # Convert all values to str
    return JsonResponse(filtered_meta)


def home_view(request):
    """
    Returns the home page data in JSON. This page is accessible after a user is authenticated.
    """
    if not request.user.is_authenticated:
        return redirect("login")

    user = request.user
    try:
        social = user.social_auth.filter(provider="google-oauth2").first()
    except AttributeError:
        return JsonResponse({"error": "No social auth found"}, status=404)

    if social is None:
        return JsonResponse({"error": "No social auth found"}, status=404)

    data = {
        "provider": social.provider,
        "uid": social.uid,
        "email": social.extra_data.get("email"),
        "name": social.extra_data.get("name"),
        "picture": social.extra_data.get("picture"),
        "extra_data": social.extra_data,  # optional, full data dump
    }

    return JsonResponse({"social_auth": data})


def logout_view(request):
    """
    Logs the user out and redirects to the login page.
    """
    logout(request)
    return redirect("login")


class GoogleCredentialAPIView(APIView):
    # permission_classes = [IsAdminUser]  # Restrict to admin users

    def get_object(self):
        try:
            return GoogleCredential.objects.get()
        except GoogleCredential.DoesNotExist:
            return None

    def get(self, request, *args, **kwargs):
        credential = self.get_object()
        if credential:
            serializer = GoogleCredentialSerializer(credential)
            return Response(serializer.data)
        return Response({"detail": "Google credentials not found."}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, *args, **kwargs):
        if self.get_object():
            return Response({"detail": "Google credentials already exist. Use PUT to update."}, status=status.HTTP_409_CONFLICT)
        serializer = GoogleCredentialSerializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except ValueError as e:  # Catch the single instance enforcement error
                return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, *args, **kwargs):
        credential = self.get_object()
        if not credential:
            return Response({"detail": "Google credentials not found. Use POST to create."}, status=status.HTTP_404_NOT_FOUND)
        serializer = GoogleCredentialSerializer(credential, data=request.data, partial=False)  # partial=False for full update
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
