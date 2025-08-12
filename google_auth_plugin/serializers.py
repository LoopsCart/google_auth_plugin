# core_settings/serializers.py
from rest_framework import serializers

from .models import GoogleCredential


class GoogleCredentialSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoogleCredential
        fields = "__all__"
