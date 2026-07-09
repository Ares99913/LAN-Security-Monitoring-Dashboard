from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.contrib.auth import authenticate, login
from datetime import timedelta
import json
from .models import Machine, Alert, BannedIP, ManagedSwitch, SwitchPort


def dashboard_view(request):
    return render(request, 'monitor/dashboard.html')


# ──────────────────────────────────────────────────
# LOGIN API
# ──────────────────────────────────────────────────
@csrf_exempt
def login_api(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST only'}, status=405)
    try:
        data     = json.loads(request.body)
        username = data.get('username', '')
        password = data.get('password', '')
        user     = authenticate(request, username=username, password=password)
        if user is None:
            return JsonResponse({'error': 'Invalid credentials'}, status=401)
        login(request, user)
        return JsonResponse({'status': 'login success'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# ──────────────────────────────────────────────────
# HEARTBEAT — Agent data receive
# ──────────────────────────────────────────────────
@csrf_exempt
def heartbeat(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST only'}, status=405)
    try:
        data = json.loads(request.body)

        machine, created = Machine.objects.get_or_create(
            ip_address=data['ip_address'],
            defaults={'hostname': data['hostname']}
        )

        if not created and machine.status == 'offline':
            Alert.objects.create(
                hostname      = data['hostname'],
                ip_address    = data['ip_address'],
                alert_type    = 'MACHINE_ONLINE',
                alert_message = f"{data['hostname']} wapas ONLINE ho gaya!"
            )

        Machine.objects.filter(ip_address=data['ip_address']).update(
            hostname           = data.get('hostname', ''),
            mac_address        = data.get('mac_address', ''),
            os_info            = data.get('os_info', ''),
            windows_version    = data.get('windows_version', ''),
            device_type        = data.get('device_type', 'PC'),
            hardware_info      = data.get('hardware_info', '{}'),
            agent_version      = data.get('agent_version', '2.0'),
            cpu_percent        = data.get('cpu_percent', 0),
            ram_percent        = data.get('ram_percent', 0),
            ram_total_gb       = data.get('ram_total_gb', 0),
            disk_percent       = data.get('disk_percent', 0),
            usb_devices        = json.dumps(data.get('usb_devices', [])),
            usb_count          = data.get('usb_count', 0),
            net_sent_mb        = data.get('net_sent_mb', 0),
            net_recv_mb        = data.get('net_recv_mb', 0),
            open_ports         = data.get('open_ports', '[]'),
            open_ports_count   = data.get('open_ports_count', 0),
            running_apps       = data.get('running_apps', '[]'),
            running_apps_count = data.get('running_apps_count', 0),
            uptime_seconds     = data.get('uptime_seconds', 0),
            status             = 'online',
        )

        if data.get('cpu_percent', 0) > 85:
            Alert.objects.create(
                hostname      = data['hostname'],
                ip_address    = data['ip_address'],
                alert_type    = 'HIGH_CPU',
                alert_message = f"HIGH CPU: {data['cpu_percent']}% on {data['hostname']}"
            )

        return JsonResponse({'status': 'ok'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# ──────────────────────────────────────────────────
# RECEIVE ALERT
# ──────────────────────────────────────────────────
@csrf_exempt
def receive_alert(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST only'}, status=405)
    try:
        data = json.loads(request.body)
        Alert.objects.create(
            hostname      = data['hostname'],
            ip_address    = data['ip_address'],
            alert_type    = data['alert_type'],
            alert_message = data['alert_message'],
            device_info   = data.get('device_info', '')
        )
        return JsonResponse({'status': 'saved'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# ──────────────────────────────────────────────────
# DASHBOARD DATA
# ──────────────────────────────────────────────────
def get_dashboard_data(request):
    # 10 sec mein heartbeat nahi = offline
    cutoff = timezone.now() - timedelta(seconds=10)
    for m in Machine.objects.filter(last_seen__lt=cutoff, status='online'):
        m.status = 'offline'
        m.save()
        Alert.objects.create(
            hostname      = m.hostname,
            ip_address    = m.ip_address,
            alert_type    = 'MACHINE_OFFLINE',
            alert_message = f"{m.hostname} OFFLINE ho gaya!"
        )

    machines = list(Machine.objects.all().values())
    alerts   = list(Alert.objects.filter(is_read=False).values()[:50])

    # Active unique ports
    all_ports = set()
    for m in machines:
        try:
            ports = json.loads(m.get('open_ports', '[]'))
            all_ports.update(ports)
        except:
            pass

    # Active IP count
    active_ips = list(
        Machine.objects.filter(status='online')
        .values_list('ip_address', flat=True)
    )

    # Switch data
    switches     = list(ManagedSwitch.objects.all().values())
    switch_ports = list(SwitchPort.objects.all().values())

    data = {
        'machines'        : machines,
        'alerts'          : alerts,
        'total'           : Machine.objects.count(),
        'online'          : Machine.objects.filter(status='online').count(),
        'offline'         : Machine.objects.filter(status='offline').count(),
        'total_ports'     : len(all_ports),
        'active_ip_count' : len(active_ips),   
        'switches'        : switches,
        'switch_ports'    : switch_ports,
    }

    return HttpResponse(
        json.dumps(data, default=str),
        content_type='application/json'
    )


# ──────────────────────────────────────────────────
# BAN / UNBAN
# ──────────────────────────────────────────────────
@csrf_exempt
def unban_ip(request, ip):
    BannedIP.objects.filter(ip_address=ip).update(is_active=False)
    return JsonResponse({'status': 'unbanned', 'ip': ip})


def get_banned_ips(request):
    banned = list(
        BannedIP.objects.filter(is_active=True).values(
            'ip_address', 'reason', 'banned_at'
        )
    )
    return HttpResponse(
        json.dumps({'banned_ips': banned}, default=str),
        content_type='application/json'
    )


@csrf_exempt
def mark_alerts_read(request):
    Alert.objects.all().update(is_read=True)
    return JsonResponse({'status': 'ok'})


# ──────────────────────────────────────────────────
# SWITCH DATA API
# ──────────────────────────────────────────────────
def get_switch_data(request):
    switches = []
    for sw in ManagedSwitch.objects.all():
        ports = list(sw.ports.values())
        switches.append({
            'id'          : sw.id,
            'name'        : sw.name,
            'ip_address'  : sw.ip_address,
            'location'    : sw.location,
            'total_ports' : sw.total_ports,
            'active_ports': sw.active_ports,
            'status'      : sw.status,
            'last_polled' : str(sw.last_polled),
            'ports'       : ports,
        })
    return HttpResponse(
        json.dumps({'switches': switches}, default=str),
        content_type='application/json'
    )


# ──────────────────────────────────────────────────
# TRACEROUTE APIs
# ──────────────────────────────────────────────────
from .models import TraceRoute, TraceHop

def get_traceroute_data(request):
    """Sabhi switches ki latest traceroute return karo"""
    from .models import ManagedSwitch
    result = []

    for sw in ManagedSwitch.objects.filter(is_active=True):
        # Latest trace
        latest = TraceRoute.objects.filter(
            target_ip=sw.ip_address
        ).first()

        if latest:
            hops = list(latest.hops.values(
                'hop_number', 'ip_address', 'hostname',
                'rtt1_ms', 'rtt2_ms', 'rtt3_ms',
                'avg_rtt_ms', 'is_timeout'
            ))
            result.append({
                'switch_name' : sw.name,
                'switch_ip'   : sw.ip_address,
                'trace_id'    : latest.id,
                'status'      : latest.status,
                'total_hops'  : latest.total_hops,
                'total_rtt_ms': latest.total_rtt_ms,
                'timestamp'   : str(latest.timestamp),
                'hops'        : hops,
            })
        else:
            result.append({
                'switch_name' : sw.name,
                'switch_ip'   : sw.ip_address,
                'trace_id'    : None,
                'status'      : 'pending',
                'total_hops'  : 0,
                'total_rtt_ms': 0,
                'timestamp'   : None,
                'hops'        : [],
            })

    return HttpResponse(
        json.dumps({'traceroutes': result}, default=str),
        content_type='application/json'
    )


@csrf_exempt
def run_traceroute_now(request, ip):
    """Manual traceroute chalao — button click pe"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST only'}, status=405)
    try:
        from .traceroute_monitor import trace_switch
        from .models import ManagedSwitch
        sw = ManagedSwitch.objects.filter(ip_address=ip).first()
        if not sw:
            # Switch nahi hai toh bhi trace karo
            class TempSwitch:
                name       = ip
                ip_address = ip
            trace_switch(TempSwitch())
        else:
            trace_switch(sw)
        return JsonResponse({'status': 'ok', 'message': f'{ip} trace complete'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
