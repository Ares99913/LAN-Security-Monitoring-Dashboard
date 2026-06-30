from django.apps import AppConfig

class MonitorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'monitor'

    def ready(self):
        import os
        if os.environ.get('RUN_MAIN') != 'true': 
            from .dns_monitor import run_dns_monitor
            run_dns_monitor()
