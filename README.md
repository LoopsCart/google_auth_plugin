# To install google-auth-app

```python
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # add these two
    "google_auth_app",
    "social_django",
]

AUTHENTICATION_BACKENDS = (
    "google_auth_app.backends.DynamicGoogleOAuth2",
    "django.contrib.auth.backends.ModelBackend",
    # "social_core.backends.google.GoogleOAuth2",
)

# this might not work, but keep
LOGIN_REDIRECT_URL = "/home/"
# this definitely works
SOCIAL_AUTH_LOGIN_REDIRECT_URL = "/home/"

# to get data from google or something like that
SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE = [
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "openid",
]

SOCIAL_AUTH_GOOGLE_OAUTH2_IGNORE_DEFAULT_SCOPE = True
SOCIAL_AUTH_GOOGLE_OAUTH2_EXTRA_DATA = ["id", "email", "name", "picture"]

```


## To configure logging

```python
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        # Log everything from your app
        "google_auth_app": {
            "handlers": ["console"],
            "level": "DEBUG",
        },
        # Log all third-party backends (optional)
        "social_core": {
            "handlers": ["console"],
            "level": "DEBUG",
        },
    },
}
```
