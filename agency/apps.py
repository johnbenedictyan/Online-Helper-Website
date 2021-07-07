from django.apps import AppConfig


class AgencyConfig(AppConfig):
    name = 'agency'

    def ready(self):
        import agency.signals
