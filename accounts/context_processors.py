from django.conf import settings


def common(request):
    """Small globals available in all templates."""
    return {
        "GOOGLE_OAUTH_ENABLED": bool(
            getattr(settings, "GOOGLE_OAUTH_CLIENT_ID", None)
            and getattr(settings, "GOOGLE_OAUTH_CLIENT_SECRET", None)
        ),
    }
