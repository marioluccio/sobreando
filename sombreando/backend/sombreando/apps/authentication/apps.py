from django.apps import AppConfig


class AuthenticationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sombreando.apps.authentication'
    verbose_name = 'Authentication'

    def ready(self):
        import sombreando.apps.authentication.signals

