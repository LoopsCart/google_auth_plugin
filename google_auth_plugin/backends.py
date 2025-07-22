# import logging

from social_core.backends.google import GoogleOAuth2

from google_auth_app.models import GoogleCredential

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
