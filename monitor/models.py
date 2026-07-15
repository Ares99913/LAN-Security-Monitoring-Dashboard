from django.db import models

# ──────────────────────────────────────────────────
# MACHINE — Connected Agents
# ──────────────────────────────────────────────────
class Machine(models.Model):
    hostname             = models.CharField(max_length=100, default='')
    ip_address           = models.CharField(max_length=20, unique=True)
    mac_address          = models.CharField(max_length=20, default='')
    os_info              = models.CharField(max_length=200, default='')
    windows_version      = models.CharField(max_length=200, default='')
    device_type          = models.CharField(max_length=50, default='PC')
    hardware_info        = models.TextField(default='{}')
    agent_version        = models.CharField(max_length=20, default='2.0')
    cpu_percent          = models.FloatField(default=0)
    ram_percent          = models.FloatField(default=0)
    ram_total_gb         = models.FloatField(default=0)
    disk_percent         = models.FloatField(default=0)
    net_sent_mb          = models.FloatField(default=0)
    net_recv_mb          = models.FloatField(default=0)
    open_ports           = models.TextField(default='[]')
    open_ports_count     = models.IntegerField(default=0)
    usb_devices          = models.TextField(default='[]')
    usb_count            = models.IntegerField(default=0)
    running_apps         = models.TextField(default='[]')
    running_apps_count   = models.IntegerField(default=0)
    uptime_seconds       = models.FloatField(default=0)
    status               = models.CharField(max_length=20, default='offline')
    first_seen           = models.DateTimeField(auto_now_add=True)
    last_seen            = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.hostname} | {self.ip_address} | {self.status}"

# ──────────────────────────────────────────────────
# ALERT
# ──────────────────────────────────────────────────
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

# ──────────────────────────────────────────────────
# BANNED IP
# ──────────────────────────────────────────────────
class BannedIP(models.Model):
    ip_address = models.CharField(max_length=20, unique=True)
    reason     = models.CharField(max_length=200)
    is_active  = models.BooleanField(default=True)
    banned_at  = models.DateTimeField(auto_now_add=True)
    auto_unban_at = models.DateTimeField(null=True, blank=True)
    unbanned_at = models.DateTimeField(null=True, blank=True)
    failed_attempts = models.IntegerField(default=0)

# ──────────────────────────────────────────────────
# SECURITY ALERT
# ──────────────────────────────────────────────────
class SecurityAlert(models.Model):
    ip_address = models.CharField(max_length=20)
    alert_type = models.CharField(max_length=50)
    message    = models.TextField()
    timestamp  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

# ──────────────────────────────────────────────────
# MANAGED SWITCH
# ──────────────────────────────────────────────────
class ManagedSwitch(models.Model):
    name         = models.CharField(max_length=100)
    ip_address   = models.CharField(max_length=20, unique=True)
    community    = models.CharField(max_length=50, default='public')
    location     = models.CharField(max_length=200, default='')
    total_ports  = models.IntegerField(default=0)
    active_ports = models.IntegerField(default=0)
    status       = models.CharField(max_length=20, default='unknown')
    is_active    = models.BooleanField(default=True)
    last_polled  = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} | {self.ip_address}"

# ──────────────────────────────────────────────────
# SWITCH PORT
# ──────────────────────────────────────────────────
class SwitchPort(models.Model):
    switch         = models.ForeignKey(
        ManagedSwitch, on_delete=models.CASCADE, related_name='ports'
    )
    if_index       = models.IntegerField()
    name           = models.CharField(max_length=50, default='')
    status         = models.CharField(max_length=20, default='down')
    speed_mbps     = models.FloatField(default=0)
    connected_macs = models.TextField(default='[]')
    mac_count      = models.IntegerField(default=0)
    last_updated   = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['switch', 'if_index']

    def __str__(self):
        return f"{self.switch.name} Port {self.if_index} | {self.status}"

# ──────────────────────────────────────────────────
# TRACEROUTE — Server se Switch tak path
# ──────────────────────────────────────────────────
class TraceRoute(models.Model):
    target_ip    = models.CharField(max_length=20)
    target_name  = models.CharField(max_length=100, default='')
    timestamp    = models.DateTimeField(auto_now_add=True)
    status       = models.CharField(max_length=20, default='pending')
    total_hops   = models.IntegerField(default=0)
    total_rtt_ms = models.FloatField(default=0)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"Trace → {self.target_ip} | {self.total_hops} hops | {self.status}"

# ──────────────────────────────────────────────────
# TRACE HOP — Har hop ka data
# ──────────────────────────────────────────────────
class TraceHop(models.Model):
    traceroute  = models.ForeignKey(
        TraceRoute, on_delete=models.CASCADE, related_name='hops'
    )
    hop_number  = models.IntegerField()
    ip_address  = models.CharField(max_length=50, default='*')
    hostname    = models.CharField(max_length=200, default='')
    rtt1_ms     = models.FloatField(default=0)
    rtt2_ms     = models.FloatField(default=0)
    rtt3_ms     = models.FloatField(default=0)
    avg_rtt_ms  = models.FloatField(default=0)
    is_timeout  = models.BooleanField(default=False)

    class Meta:
        ordering = ['hop_number']

    def __str__(self):
        return f"Hop {self.hop_number} → {self.ip_address} ({self.avg_rtt_ms}ms)"
