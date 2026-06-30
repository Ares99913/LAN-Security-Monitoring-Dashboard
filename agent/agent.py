import psutil, requests, time
import socket, platform
import datetime, subprocess
import json, uuid

SERVER_IP = "10.107.159.30"
SERVER_PORT = 8000
INTERVAL    = 3

SERVER   = f"http://{SERVER_IP}:{SERVER_PORT}"
prev_usb = set()

def get_mac():
    return ':'.join(['{:02x}'.format(
        (uuid.getnode() >> i) & 0xff
    ) for i in range(0,48,8)][::-1])

def get_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect((SERVER_IP, SERVER_PORT))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return socket.gethostbyname(socket.gethostname())

def get_usb():
    try:
        if platform.system() == "Windows":
            r = subprocess.run(
                [
                    "powershell",
                    "-NoProfile",
                    "-Command",
                    "Get-CimInstance Win32_LogicalDisk | "
                    "Where-Object {$_.DriveType -eq 2} | "
                    "ForEach-Object { $_.DeviceID + ' ' + $_.VolumeName }"
                ],
                capture_output=True,
                text=True,
                timeout=5
            )
            return set(
                l.strip() for l in r.stdout.splitlines()
                if l.strip()
            )
        else:
            r = subprocess.run(
                ['lsusb'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return set(
                l.strip() for l in r.stdout.split('\n')
                if l.strip()
            )
    except Exception as e:
        print(f"[USB ERR] {e}")
        return set()

def send_alert(hostname, ip, atype, msg, info=""):
    try:
        requests.post(f"{SERVER}/api/alert/", json={
            'hostname'     : hostname,
            'ip_address'   : ip,
            'alert_type'   : atype,
            'alert_message': msg,
            'device_info'  : info
        }, timeout=3)
    except:
        pass

def run():
    global prev_usb
    hostname = socket.gethostname()
    ip       = get_ip()
    mac      = get_mac()
    os_info  = f"{platform.system()} {platform.release()}"

    prev_usb = get_usb()

    print(f"\n{'='*45}")
    print(f"  509 SERVER AGENT")
    print(f"  Machine : {hostname}")
    print(f"  IP      : {ip}")
    print(f"  MAC     : {mac}")
    print(f"  Server  : {SERVER}")
    print(f"{'='*45}\n")

    while True:
        try:
            curr_usb = get_usb()

            for dev in (curr_usb - prev_usb):
                print(f"[USB IN] {dev}")
                send_alert(hostname, ip,
                    'USB_CONNECTED',
                    f'USB IN: {dev}', dev)

            for dev in (prev_usb - curr_usb):
                print(f"[USB OUT] {dev}")
                send_alert(hostname, ip,
                    'USB_DISCONNECTED',
                    f'USB OUt: {dev}', dev)

            prev_usb = curr_usb

            cpu  = psutil.cpu_percent(interval=1)
            ram  = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            net  = psutil.net_io_counters()

            data = {
                'hostname'    : hostname,
                'ip_address'  : ip,
                'mac_address' : mac,
                'os_info'     : os_info,
                'cpu_percent' : cpu,
                'ram_percent' : ram.percent,
                'ram_total_gb': round(ram.total/1024**3, 2),
                'disk_percent': disk.percent,
                'usb_devices' : list(curr_usb),
                'usb_count'   : len(curr_usb),
                'net_sent_mb' : round(net.bytes_sent/1024**2, 2),
                'net_recv_mb' : round(net.bytes_recv/1024**2, 2),
            }

            r = requests.post(
                f"{SERVER}/api/heartbeat/",
                json=data, timeout=5
            )

            if r.status_code == 200:
                print(f"[OK] CPU:{cpu}% "
                      f"RAM:{ram.percent}% "
                      f"USB:{len(curr_usb)} "
                      f"| {hostname}")
            else:
                print(f"[ERR] {r.status_code}")

        except requests.exceptions.ConnectionError:
            print("[!] Server nahi mila — retry...")
        except Exception as e:
            print(f"[ERR] {e}")

        time.sleep(INTERVAL)

if __name__ == "__main__":
    run()