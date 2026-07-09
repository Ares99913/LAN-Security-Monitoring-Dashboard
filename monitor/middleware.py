from datetime import timedelta

from django.core.cache import cache
from django.http import JsonResponse
from django.utils import timezone

from .models import Alert, BannedIP


class BruteForceMiddleware:
    MAX_ATTEMPTS = 4
    WINDOW_SECONDS = 300
    BAN_MINUTES = 15

    def __init__(self, get_response):
        self.get_response = get_response

    def get_client_ip(self, request):
        forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR", "")

    def get_cache_key(self, ip):
        return f"fail_{ip}"

    def auto_unban_if_expired(self, banned_ip):
        if not banned_ip.auto_unban_at:
            return False

        if timezone.now() < banned_ip.auto_unban_at:
            return False

        banned_ip.is_active = False
        banned_ip.unbanned_at = timezone.now()
        banned_ip.save(update_fields=["is_active", "unbanned_at"])

        Alert.objects.create(
            hostname="Server",
            ip_address=banned_ip.ip_address,
            alert_type="AUTO_UNBAN",
            alert_message=f"AUTO UNBAN: {banned_ip.ip_address} ban duration expired"
        )

        return True

    def __call__(self, request):
        ip = self.get_client_ip(request)

        if ip:
            banned_ip = BannedIP.objects.filter(
                ip_address=ip,
                is_active=True
            ).first()

            if banned_ip:
                if not self.auto_unban_if_expired(banned_ip):
                    return JsonResponse(
                        {
                            "error": "IP Banned!",
                            "ip": ip,
                            "reason": banned_ip.reason,
                            "auto_unban_at": banned_ip.auto_unban_at,
                        },
                        status=403
                    )

        response = self.get_response(request)

        if request.method == "POST" and response.status_code == 401 and ip:
            key = self.get_cache_key(ip)
            attempts = cache.get(key, 0) + 1
            cache.set(key, attempts, timeout=self.WINDOW_SECONDS)

            if attempts >= self.MAX_ATTEMPTS:
                auto_unban_at = timezone.now() + timedelta(
                    minutes=self.BAN_MINUTES
                )

                banned_ip, created = BannedIP.objects.get_or_create(
                    ip_address=ip,
                    defaults={
                        "reason": "Brute Force",
                        "is_active": True,
                        "failed_attempts": attempts,
                        "auto_unban_at": auto_unban_at,
                    }
                )

                if not created:
                    banned_ip.reason = "Brute Force"
                    banned_ip.is_active = True
                    banned_ip.failed_attempts = attempts
                    banned_ip.auto_unban_at = auto_unban_at
                    banned_ip.unbanned_at = None
                    banned_ip.save()

                Alert.objects.create(
                    hostname="Unknown",
                    ip_address=ip,
                    alert_type="BRUTE_FORCE",
                    alert_message=(
                        f"BANNED: {ip} - {self.MAX_ATTEMPTS} wrong attempts. "
                        f"Auto-unban after {self.BAN_MINUTES} minutes."
                    )
                )

                cache.delete(key)

        return response
