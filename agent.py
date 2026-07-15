import json
import os
import platform
import socket
import subprocess
import sys
import time
import uuid
from datetime import datetime
from pathlib import Path

import psutil
import requests

SERVER_IP = "192.168.1.6"
SERVER_PORT = 8080
INTERVAL = 3

AGENT_VERSION = "2.0"
MAX_PROCESSES = 80
MAX_PORTS = 150
MAX_HARDWARE = 80
MAX_ACTIVE_IPS = 80

SERVER = f"http://{SERVER_IP}:{SERVER_PORT}"
prev_usb = set()
agent_started_at = time.time()


def _crash_log_path():
    try:
        base = Path(sys.executable).parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parent
        return base / "agent_crash.log"
    except Exception:
        return Path("agent_crash.log")


def log_error(msg: str):
    try:
        p = _crash_log_path()
        existing = ""
        try:
            if p.exists():
                existing = p.read_text(encoding="utf-8")
        except Exception:
            existing = ""
        p.write_text(existing + f"[{datetime.now().isoformat()}] {msg}\n", encoding="utf-8")
    except Exception:
        pass

    try:
        print(msg)
    except Exception:
        pass


def exe_path():
    if getattr(sys, "frozen", False):
        return sys.executable
    return str(Path(__file__).resolve())


def install_startup():
    if platform.system() != "Windows":
        print("[STARTUP] Auto startup only supported on Windows.")
        return

    try:
        startup_dir = Path(os.environ["APPDATA"]) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
        startup_dir.mkdir(parents=True, exist_ok=True)

        bat_path = startup_dir / "509-agent-startup.bat"
        bat_path.write_text(f'@echo off\nstart "" "{exe_path()}"\n', encoding="utf-8")

        print(f"[STARTUP] Installed: {bat_path}")
    except Exception as e:
        print(f"[STARTUP ERR] {e}")


def uninstall_startup():
    if platform.system() != "Windows":
        return

    try:
        startup_dir = Path(os.environ["APPDATA"]) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
        bat_path = startup_dir / "509-agent-startup.bat"

        if bat_path.exists():
            bat_path.unlink()
            print("[STARTUP] Removed.")
        else:
            print("[STARTUP] Not installed.")
    except Exception as e:
        print(f"[STARTUP ERR] {e}")


def run_cmd(command, timeout=8):
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
            shell=False,
        )
        return result.stdout.strip()
    except Exception:
        return ""


def run_powershell(script, timeout=8):
    return run_cmd(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script],
        timeout=timeout,
    )


def get_mac():
    return ":".join(
        ["{:02x}".format((uuid.getnode() >> i) & 0xff) for i in range(0, 48, 8)][::-1]
    )


def get_ip():
    target_prefix = ".".join(SERVER_IP.split(".")[:3]) + "."

    try:
        for nic, addrs in psutil.net_if_addrs().items():
            for addr in addrs:
                if addr.family == socket.AF_INET:
                    ip = addr.address
                    if ip.startswith(target_prefix):
                        return ip
    except Exception:
        pass

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect((SERVER_IP, SERVER_PORT))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return socket.gethostbyname(socket.gethostname())


def get_os_info():
    return f"{platform.system()} {platform.release()} {platform.version()}"


def get_device_type():
    system = platform.system().lower()

    if "windows" in system:
        return "Windows PC"
    if "linux" in system:
        return "Linux PC"
    if "darwin" in system:
        return "Mac"
    return "Unknown"


def get_disk_usage():
    # Windows root path must be a proper string literal.
    path = "C:\\" if platform.system() == "Windows" else "/"
    try:
        return psutil.disk_usage(path)
    except Exception:
        return psutil.disk_usage("/")


def get_usb():
    try:
        if platform.system() == "Windows":
            script = (
                "Get-CimInstance Win32_LogicalDisk | "
                "Where-Object {$_.DriveType -eq 2} | "
                "ForEach-Object { $_.DeviceID + ' ' + $_.VolumeName }"
            )
            output = run_powershell(script, timeout=5)
            return set(line.strip() for line in output.splitlines() if line.strip())

        output = run_cmd(["lsusb"], timeout=5)
        return set(line.strip() for line in output.splitlines() if line.strip())

    except Exception as e:
        log_error(f"[USB ERR] {e}")
        return set()


def get_open_ports():
    ports = []

    try:
        for conn in psutil.net_connections(kind="inet"):
            if conn.status != psutil.CONN_LISTEN or not conn.laddr:
                continue

            item = {
                "ip": conn.laddr.ip,
                "port": conn.laddr.port,
                "protocol": "TCP",
                "pid": conn.pid,
                "process": "",
            }

            if conn.pid:
                try:
                    item["process"] = psutil.Process(conn.pid).name()
                except Exception:
                    item["process"] = ""

            ports.append(item)

        unique = {}
        for item in ports:
            key = f"{item['ip']}:{item['port']}:{item['protocol']}"
            unique[key] = item

        return list(unique.values())[:MAX_PORTS]

    except Exception as e:
        log_error(f"[PORT ERR] {e}")
        return []


def get_running_processes():
    processes = []

    try:
        for proc in psutil.process_iter(["pid", "name", "username", "status"]):
            info = proc.info
            processes.append(
                {
                    "pid": info.get("pid"),
                    "name": info.get("name") or "",
                    "username": info.get("username") or "",
                    "status": info.get("status") or "",
                }
            )

        processes.sort(key=lambda p: (p["name"] or "").lower())
        return processes[:MAX_PROCESSES]

    except Exception as e:
        log_error(f"[PROC ERR] {e}")
        return []


def get_hardware_devices():
    devices = []

    try:
        if platform.system() == "Windows":
            script = (
                "Get-CimInstance Win32_PnPEntity | "
                "Where-Object {$_.Name -ne $null} | "
                "Select-Object -First 80 Name,PNPClass,Status | "
                "ForEach-Object { ($_.PNPClass + ' | ' + $_.Name + ' | ' + $_.Status) }"
            )
            output = run_powershell(script, timeout=10)
            for line in output.splitlines():
                line = line.strip()
                if line:
                    devices.append(line)
        else:
            output = run_cmd(["sh", "-c", "lsblk -o NAME,TYPE,SIZE,MODEL 2>/dev/null"], timeout=5)
            devices = [line.strip() for line in output.splitlines() if line.strip()]

    except Exception as e:
        log_error(f"[HW ERR] {e}")

    return devices[:MAX_HARDWARE]


def get_active_ips():
    active = []

    try:
        if platform.system() == "Windows":
            output = run_cmd(["arp", "-a"], timeout=5)
        else:
            output = run_cmd(["ip", "neigh"], timeout=5)

        for line in output.splitlines():
            line = line.strip()
            if not line:
                continue

            parts = line.replace("(", " ").replace(")", " ").split()
            for part in parts:
                if part.count(".") == 3:
                    active.append(part)
                    break

        return sorted(list(set(active)))[:MAX_ACTIVE_IPS]

    except Exception as e:
        log_error(f"[ARP ERR] {e}")
        return []


def send_alert(hostname, ip, alert_type, message, info=""):
    try:
        response = requests.post(
            f"{SERVER}/api/alert/",
            json={
                "hostname": hostname,
                "ip_address": ip,
                "alert_type": alert_type,
                "alert_message": message,
                "device_info": info,
            },
            timeout=3,
        )

        if response.status_code != 200:
            log_error(f"[ALERT ERR] {response.status_code} {response.text[:160]}")

    except Exception as e:
        log_error(f"[ALERT SEND ERR] {e}")


def post_heartbeat(data):
    return requests.post(f"{SERVER}/api/heartbeat/", json=data, timeout=5)


def run():
    global prev_usb

    hostname = socket.gethostname()
    mac = get_mac()
    os_info = get_os_info()
    device_type = get_device_type()

    prev_usb = get_usb()

    print(f"\n{'=' * 52}")
    print("  509 SERVER AGENT v2")
    print(f"  Machine : {hostname}")
    print(f"  IP      : {get_ip()}")
    print(f"  MAC     : {mac}")
    print(f"  OS      : {os_info}")
    print(f"  Type    : {device_type}")
    print(f"  Server  : {SERVER}")
    print(f"{'=' * 52}\n")

    while True:
        try:
            ip = get_ip()
            curr_usb = get_usb()

            for device in curr_usb - prev_usb:
                print(f"[USB IN] {device}")
                send_alert(hostname, ip, "USB_CONNECTED", f"USB connected: {device}", device)

            for device in prev_usb - curr_usb:
                print(f"[USB OUT] {device}")
                send_alert(hostname, ip, "USB_DISCONNECTED", f"USB disconnected: {device}", device)

            prev_usb = curr_usb

            cpu = psutil.cpu_percent(interval=1)
            ram = psutil.virtual_memory()
            disk = get_disk_usage()
            net = psutil.net_io_counters()

            open_ports = get_open_ports()
            processes = get_running_processes()
            hardware = get_hardware_devices()
            active_ips = get_active_ips()

            uptime_seconds = int(time.time() - agent_started_at)
            boot_time = datetime.fromtimestamp(psutil.boot_time()).isoformat()

            data = {
                "hostname": hostname,
                "ip_address": ip,
                "mac_address": mac,
                "os_info": os_info,
                "windows_version": platform.version() if platform.system() == "Windows" else "",
                "device_type": device_type,
                "agent_version": AGENT_VERSION,
                "cpu_percent": cpu,
                "ram_percent": ram.percent,
                "ram_total_gb": round(ram.total / 1024 ** 3, 2),
                "disk_percent": disk.percent,
                "usb_devices": list(curr_usb),
                "usb_count": len(curr_usb),
                "net_sent_mb": round(net.bytes_sent / 1024 ** 2, 2),
                "net_recv_mb": round(net.bytes_recv / 1024 ** 2, 2),
                "open_ports": json.dumps(open_ports),
                "open_ports_count": len(open_ports),
                "running_apps": json.dumps(processes),
                "running_apps_count": len(processes),
                "hardware_info": json.dumps(hardware),
                "active_ips": active_ips,
                "active_ips_count": len(active_ips),
                "uptime_seconds": uptime_seconds,
                "system_boot_time": boot_time,
            }

            response = post_heartbeat(data)

            if response.status_code == 200:
                print(
                    f"[OK] CPU:{cpu}% RAM:{ram.percent}% USB:{len(curr_usb)} PORTS:{len(open_ports)} "
                    f"PROC:{len(processes)} IPs:{len(active_ips)} | {hostname}"
                )
            else:
                log_error(f"[ERR] Server {response.status_code}: {response.text[:140]}")

        except requests.exceptions.ConnectionError:
            print("[!] Server not found")
        except Exception as e:
            log_error(f"[ERR] {type(e).__name__}: {e}")

        time.sleep(INTERVAL)


if __name__ == "__main__":
    try:
        if "--install-startup" in sys.argv:
            install_startup()
        elif "--uninstall-startup" in sys.argv:
            uninstall_startup()
        else:
            run()
    except Exception as e:
        log_error(f"FATAL: {type(e).__name__}: {e}")

