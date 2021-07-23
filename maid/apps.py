from django.apps import AppConfig


class MaidConfig(AppConfig):
    name = 'maid'

    def ready(self):
        import maid.signals
