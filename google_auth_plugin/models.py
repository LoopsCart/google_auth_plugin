from django.db import models


class GoogleCredential(models.Model):
    client_id = models.CharField(max_length=255, unique=True, help_text="Google OAuth2 Client ID")
    client_secret = models.CharField(max_length=255, help_text="Google OAuth2 Client Secret")
    redirect_uri = models.URLField(max_length=255, blank=True, null=True)

    def save(self, *args, **kwargs):
        existing = GoogleCredential.objects.first()
        if existing and not self.pk:
            self.pk = existing.pk  # overwrite existing instead of creating new
        super().save(*args, **kwargs)

    def __str__(self):
        return "Google OAuth2 Credentials"

    class Meta:
        verbose_name_plural = "Google Credentials"
