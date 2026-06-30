from django.db import models

from django.db import models

class Machine(models.Model):
    hostname     = models.CharField(max_length=100, default='')
    ip_address   = models.CharField(max_length=20, unique=True)
    mac_address  = models.CharField(max_length=20, default='')
    os_info      = models.CharField(max_length=200, default='')
    cpu_percent  = models.FloatField(default=0)
    ram_percent  = models.FloatField(default=0)
    ram_total_gb = models.FloatField(default=0)
    disk_percent = models.FloatField(default=0)
    usb_devices  = models.TextField(default='[]')
    usb_count    = models.IntegerField(default=0)
    net_sent_mb  = models.FloatField(default=0)
    net_recv_mb  = models.FloatField(default=0)
    status       = models.CharField(max_length=20, default='offline')
    last_seen    = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.hostname} | {self.ip_address} | {self.status}"


class Alert(models.Model):
    hostname      = models.CharField(max_length=100)
    ip_address    = models.CharField(max_length=20)
    alert_type    = models.CharField(max_length=50)
    alert_message = models.TextField()
    device_info   = models.TextField(default='')
    timestamp     = models.DateTimeField(auto_now_add=True)
    is_read       = models.BooleanField(default=False)

    class Meta:
        ordering = ['-timestamp']


class BannedIP(models.Model):
    ip_address = models.CharField(max_length=20, unique=True)
    reason     = models.CharField(max_length=200)
    is_active  = models.BooleanField(default=True)
    banned_at  = models.DateTimeField(auto_now_add=True)


class SecurityAlert(models.Model):
    ip_address = models.CharField(max_length=20)
    alert_type = models.CharField(max_length=50)
    message    = models.TextField()
    timestamp  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
