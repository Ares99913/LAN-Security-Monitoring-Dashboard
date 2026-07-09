from django.apps import AppConfig

class MonitorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'monitor'

    def ready(self):
        import os
        if os.environ.get('RUN_MAIN') != 'true':
            return

        # ── ARP Monitor ──────────────────────────
        try:
            from .arp_monitor import run_arp_monitor
            run_arp_monitor()
            print("[OK] ARP Monitor Started")
        except Exception as e:
            print(f"[ERR] ARP Monitor: {e}")

        # ── DNS Monitor ──────────────────────────
        try:
            from .dns_monitor import run_dns_monitor
            run_dns_monitor()
            print("[OK] DNS Monitor Started")
        except Exception as e:
            print(f"[ERR] DNS Monitor: {e}")

        # ── SNMP Monitor ─────────────────────────
        try:
            from .snmp_monitor import run_snmp_monitor
            run_snmp_monitor()
            print("[OK] SNMP Monitor Started")
        except Exception as e:
            print(f"[ERR] SNMP Monitor: {e}")

        # ── Traceroute Monitor ───────────────────
        try:
            from .traceroute_monitor import run_trace_monitor
            run_trace_monitor()
            print("[OK] Traceroute Monitor Started")
        except Exception as e:
            print(f"[ERR] Traceroute Monitor: {e}")
