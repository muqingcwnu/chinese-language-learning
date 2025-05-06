from django.apps import AppConfig


class MainCoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'main_core'

    def ready(self):
        # Import template tags to ensure they are registered
        import main_core.templatetags.main_core_tags
