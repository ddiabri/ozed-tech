from django.apps import AppConfig


class TicketingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ticketing'

    def ready(self):
        """Import signals when app is ready."""
        import ticketing.signals  # noqa
