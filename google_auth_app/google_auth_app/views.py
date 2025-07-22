import requests
from django.contrib.auth import logout
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import GoogleCredential
from .serializers import GoogleCredentialSerializer


def verify_google_access_token(access_token):
    """
    Verifies a Google access token by trying to fetch user info.
    """
    userinfo_url = "https://www.googleapis.com/oauth2/v2/userinfo"
    headers = {"Authorization": f"Bearer {access_token}"}
    try:
        response = requests.get(userinfo_url, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)
        user_info = response.json()
        print("Access Token is valid. User Info:", user_info)
        return user_info
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            print("Access Token is invalid or expired.")
        else:
            print(f"Error verifying access token: {e}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Network or request error: {e}")
        return None


# How you'd typically get the access token from social_auth:
# Assuming `request.user` is authenticated via google-oauth2
# if request.user.is_authenticated:
#     try:
#         social_user = request.user.social_auth.get(provider='google-oauth2')
#         access_token = social_user.extra_data.get('access_token')
#         if access_token:
#             user_details = verify_google_access_token(access_token)
#             if user_details:
#                 # Access token is good for fetching user info
#                 pass
#         else:
#             print("No access token found for this social user.")
#     except ObjectDoesNotExist:
#         print("User not authenticated via google-oauth2.")


def google_login_view(request):
    """
    Custom API endpoint to begin Google OAuth2 login.
    """
    login_url = reverse("social:begin", args=["google-oauth2"])
    return redirect(login_url)


def login_view(request):
    """
    Renders the login page
    """
    return render(request, "google_auth_app/login.html")


def home_view(request):
    """
    Returns the home page data in JSON. This page is accessible after a user is authenticated.
    """
    if not request.user.is_authenticated:
        return redirect("login")

    social = None
    user = request.user

    try:
        social = user.social_auth.filter(provider="google-oauth2").first()
    except AttributeError:
        return JsonResponse({"error": "No Google social authentication found for this user."}, status=404)

    if social is None:
        return JsonResponse({"error": "No Google social authentication found for this user."}, status=404)

    access_token = social.extra_data.get("access_token")
    if not access_token:
        return JsonResponse({"error": "No access token found for Google social auth."}, status=404)

    # --- Verify and Refresh Access Token ---
    is_token_valid = False
    google_user_info = None

    # 1. Try to verify the current access token
    google_user_info = verify_google_access_token(access_token)
    if google_user_info:
        is_token_valid = True
        # print("Access token is currently valid.")
    else:
        # print("Access token might be expired or invalid. Attempting to refresh...")
        # 2. If verification fails, try to refresh the token
        refresh_token = social.extra_data.get("refresh_token")
        if refresh_token:
            try:
                # This call will use the refresh_token to get a new access_token
                # and update social.extra_data in the database.
                social.refresh_token()
                new_access_token = social.extra_data.get("access_token")
                # print("Access token refreshed successfully.")
                # 3. Verify the new access token
                google_user_info = verify_google_access_token(new_access_token)
                if google_user_info:
                    is_token_valid = True
                    # print("New access token is valid.")
                else:
                    pass
                    # print("New access token also failed validation.")
            except Exception as e:
                # print(f"Failed to refresh access token: {e}")
                # You might want to log the user out or ask them to re-authenticate
                return JsonResponse({"error": f"Failed to refresh access token: {e}"}, status=400)
        else:
            # print("No refresh token available. User needs to re-authenticate.")
            # Optionally, you could redirect to login here,
            # but for an API endpoint, returning an error is often better.
            return JsonResponse({"error": "Access token expired and no refresh token available. Please log in again."}, status=401)

    if not is_token_valid:
        return JsonResponse({"error": "Could not validate or refresh access token. Please log in again."}, status=401)

    if google_user_info and social.extra_data.get("email") != google_user_info.get("email"):
        return JsonResponse({"error": "Email mismatch between stored and verified Google user data. Please log in again."}, status=400)

    data = {
        "provider": social.provider,
        "uid": social.uid,
        "email": social.extra_data.get("email"),
        "name": social.extra_data.get("name"),
        "picture": social.extra_data.get("picture"),
        # Include the verified user info from Google's API if available
        "google_api_user_info": google_user_info,
        # 'extra_data' might contain the newly refreshed token if it was refreshed
        "extra_data_from_social_auth": social.extra_data,
    }

    return JsonResponse({"social_auth_status": "Access token is valid and user authenticated", "user_data": data})


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
