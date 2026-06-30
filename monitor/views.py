from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.contrib.auth import authenticate, login
from datetime import timedelta
import json
from .models import Machine, Alert, BannedIP


def dashboard_view(request):
    return render(request, 'monitor/dashboard.html')


@csrf_exempt
def login_api(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST only'}, status=405)

    try:
        if request.body:
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError:
                data = request.POST
        else:
            data = request.POST

        username = data.get('username', '')
        password = data.get('password', '')

        user = authenticate(request, username=username, password=password)

        if user is None:
            return JsonResponse(
                {'error': 'Invalid credentials'},
                status=401
            )

        login(request, user)
        return JsonResponse({'status': 'login success'})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


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
                hostname=data['hostname'],
                ip_address=data['ip_address'],
                alert_type='MACHINE_ONLINE',
                alert_message=f"{data['hostname']} ONLINE!"
            )
        Machine.objects.filter(ip_address=data['ip_address']).update(
            hostname=data.get('hostname', ''),
            mac_address=data.get('mac_address', ''),
            os_info=data.get('os_info', ''),
            cpu_percent=data.get('cpu_percent', 0),
            ram_percent=data.get('ram_percent', 0),
            ram_total_gb=data.get('ram_total_gb', 0),
            disk_percent=data.get('disk_percent', 0),
            usb_devices=json.dumps(data.get('usb_devices', [])),
            usb_count=data.get('usb_count', 0),
            net_sent_mb=data.get('net_sent_mb', 0),
            net_recv_mb=data.get('net_recv_mb', 0),
            status='online'
        )
        if data.get('cpu_percent', 0) > 85:
            Alert.objects.create(
                hostname=data['hostname'],
                ip_address=data['ip_address'],
                alert_type='HIGH_CPU',
                alert_message=f"CPU {data['cpu_percent']}% CRITICAL!"
            )
        return JsonResponse({'status': 'ok'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def receive_alert(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST only'}, status=405)
    try:
        data = json.loads(request.body)
        Alert.objects.create(
            hostname=data['hostname'],
            ip_address=data['ip_address'],
            alert_type=data['alert_type'],
            alert_message=data['alert_message'],
            device_info=data.get('device_info', '')
        )
        return JsonResponse({'status': 'saved'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def get_dashboard_data(request):
    cutoff = timezone.now() - timedelta(seconds=10)
    for m in Machine.objects.filter(last_seen__lt=cutoff, status='online'):
        m.status = 'offline'
        m.save()
        Alert.objects.create(
            hostname=m.hostname,
            ip_address=m.ip_address,
            alert_type='MACHINE_OFFLINE',
            alert_message=f"{m.hostname} OFFLINE !"
        )

    machines = list(Machine.objects.all().values())
    alerts = list(Alert.objects.filter(is_read=False).values()[:30])

    data = {
        'machines': machines,
        'alerts': alerts,
        'total': Machine.objects.count(),
        'online': Machine.objects.filter(status='online').count(),
        'offline': Machine.objects.filter(status='offline').count(),
    }

    return HttpResponse(
        json.dumps(data, default=str),
        content_type='application/json'
    )


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
    data = {'banned_ips': banned}

    return HttpResponse(
        json.dumps(data, default=str),
        content_type='application/json'
    )


@csrf_exempt
def mark_alerts_read(request):
    Alert.objects.all().update(is_read=True)
    return JsonResponse({'status': 'ok'})
