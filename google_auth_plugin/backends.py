# import logging

from django.core.exceptions import ImproperlyConfigured
from social_core.backends.google import GoogleOAuth2

from google_auth_plugin.models import GoogleCredential

# logger = logging.getLogger(__name__)


class DynamicGoogleOAuth2(GoogleOAuth2):
    def setting(self, name, default=None):
        # logger.info(f"DynamicGoogleOAuth2: Fetching setting '{name}'")
        if name == "KEY" or name == "SECRET":
            try:
                config = GoogleCredential.objects.first()
                if config is not None:
                    if name == "KEY":
                        return config.client_id
                    elif name == "SECRET":
                        return config.client_secret
                else:
                    return default
            except GoogleCredential.DoesNotExist:
                return default
        return super().setting(name, default)


class TenantAwareGoogleOAuth2(GoogleOAuth2):
    def get_key_and_secret(self):
        current_domain = self.strategy.request_host()
        try:
            creds = GoogleCredential.objects.get(tenant_domain=current_domain)
            return creds.client_id, creds.client_secret
        except GoogleCredential.DoesNotExist:
            raise ImproperlyConfigured(f"No Google credentials configured for domain {current_domain}")
