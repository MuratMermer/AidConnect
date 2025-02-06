from django.apps import AppConfig


class AppsocialmediaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Appsocialmedia'

    def ready(self):
        import Appsocialmedia.signals
