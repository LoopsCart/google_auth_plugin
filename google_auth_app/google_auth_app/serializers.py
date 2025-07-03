# core_settings/serializers.py
from rest_framework import serializers

from .models import GoogleCredential


class GoogleCredentialSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoogleCredential
        fields = ["client_id", "client_secret"]  # Add 'redirect_uri' if you included it
