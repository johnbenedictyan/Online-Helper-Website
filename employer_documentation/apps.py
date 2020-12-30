from django.apps import AppConfig


class EmployerDocumentationConfig(AppConfig):
    name = 'employer_documentation'

    def ready(self):
        import employer_documentation.signals
