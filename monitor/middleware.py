from django.core.cache import cache
from django.http import JsonResponse
from .models import BannedIP, Alert


class BruteForceMiddleware:
    MAX_ATTEMPTS = 3
    WINDOW_SECONDS = 300

    def __init__(self, get_response):
        self.get_response = get_response

    def get_client_ip(self, request):
        forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR", "")

    def __call__(self, request):
        ip = self.get_client_ip(request)

        if ip and BannedIP.objects.filter(ip_address=ip, is_active=True).exists():
            return JsonResponse(
                {"error": "IP Banned!"},
                status=403
            )

        response = self.get_response(request)

        if request.method == "POST" and response.status_code == 401 and ip:
            key = f"fail_{ip}"
            attempts = cache.get(key, 0) + 1
            cache.set(key, attempts, timeout=self.WINDOW_SECONDS)

            if attempts >= self.MAX_ATTEMPTS:
                banned_ip, created = BannedIP.objects.get_or_create(
                    ip_address=ip,
                    defaults={"reason": "Brute Force", "is_active": True}
                )

                if not banned_ip.is_active:
                    banned_ip.is_active = True
                    banned_ip.reason = "Brute Force"
                    banned_ip.save()

                if created or attempts == self.MAX_ATTEMPTS:
                    Alert.objects.create(
                        hostname="Unknown",
                        ip_address=ip,
                        alert_type="BRUTE_FORCE",
                        alert_message=f"BANNED: {ip} - {self.MAX_ATTEMPTS} wrong attempts!"
                    )

                cache.delete(key)

        return response
