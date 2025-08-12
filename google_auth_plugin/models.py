from django.db import models


class GoogleCredential(models.Model):
    client_id = models.CharField(max_length=255, unique=True, help_text="Google OAuth2 Client ID")
    client_secret = models.CharField(max_length=255, help_text="Google OAuth2 Client Secret")
    redirect_uri = models.URLField(max_length=255, blank=True, null=True)

    # Enforce only one instance
    def save(self, *args, **kwargs):
        if GoogleCredential.objects.exists() and not self.pk:
            raise ValueError("There can be only one GoogleCredential instance.")
        super().save(*args, **kwargs)

    def __str__(self):
        return "Google OAuth2 Credentials"

    class Meta:
        verbose_name_plural = "Google Credentials"
