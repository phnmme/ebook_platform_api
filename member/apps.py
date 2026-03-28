from django.apps import AppConfig


class MemberConfig(AppConfig):
    name = 'member'

    def ready(self):
        # Ensure signal handlers are registered
        from . import signals  # noqa: F401
