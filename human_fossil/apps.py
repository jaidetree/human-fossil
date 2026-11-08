from django.apps import AppConfig


class HumanFossilConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "human_fossil"

    def ready(self) -> None:
        from . import thumbnails

        thumbnails.connect()
