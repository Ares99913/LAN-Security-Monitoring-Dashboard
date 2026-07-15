import subprocess
import threading
import time
import re
import platform
from django.utils import timezone

TRACE_INTERVAL = 300  # Har 5 min mein traceroute chalao

# ──────────────────────────────────────────────────
# TRACEROUTE COMMAND (Windows + Linux Compatible)
# ──────────────────────────────────────────────────
def run_traceroute(target_ip):
    try:
        is_windows = platform.system().lower() == 'windows'
        
        if is_windows:
            # Windows: tracert command
            result = subprocess.run(
                ['tracert', '-d', '-h', '20', '-w', '2000', target_ip],
                capture_output=True,
                text=True,
                timeout=60
            )
        else:
            # Linux/Unix: traceroute command
            result = subprocess.run(
                ['traceroute', '-n', '-m', '20', '-w', '2', '-q', '3', target_ip],
                capture_output=True,
                text=True,
                timeout=60
            )
        
        return result.stdout if result.returncode == 0 else result.stdout
    except subprocess.TimeoutExpired:
        return None
    except FileNotFoundError:
        print(f"[TRACE ERR] traceroute/tracert command not found")
        return None
    except Exception as e:
        print(f"[TRACE ERR] {e}")
        return None


def parse_traceroute(output):
    hops = []
    if not output:
        return hops

    is_windows = platform.system().lower() == 'windows'
    lines = output.strip().split('\n')
    
    # Skip header lines
    start_idx = 1
    for i, line in enumerate(lines):
        if 'Tracing route' in line or 'traceroute to' in line:
            start_idx = i + 1
            break

    for line in lines[start_idx:]:
        line = line.strip()
        if not line or line.startswith('Trace complete'):
            continue

        # Timeout hop: " 1    *        *        *     Request timed out." (Windows)
        # or: " 1  * * *" (Linux)
        if '*' in line:
            timeout_match = re.match(r'^\s*(\d+)\s+.*\*', line)
            if timeout_match:
                hops.append({
                    'hop_number': int(timeout_match.group(1)),
                    'ip_address': '*',
                    'hostname'  : '',
                    'rtt1_ms'   : 0,
                    'rtt2_ms'   : 0,
                    'rtt3_ms'   : 0,
                    'avg_rtt_ms': 0,
                    'is_timeout': True,
                })
                continue

        if is_windows:
            # Windows format: " 1    <1 ms    <1 ms    <1 ms  192.168.1.1"
            # or: " 2     5 ms     3 ms     4 ms  10.0.0.1"
            win_match = re.match(
                r'^\s*(\d+)\s+(?:<\s*)?(\d+)\s+ms\s+(?:<\s*)?(\d+)\s+ms\s+(?:<\s*)?(\d+)\s+ms\s+([\d.]+)',
                line
            )
            if win_match:
                hop_num = int(win_match.group(1))
                rtt1    = float(win_match.group(2))
                rtt2    = float(win_match.group(3))
                rtt3    = float(win_match.group(4))
                ip      = win_match.group(5)
                avg     = round((rtt1 + rtt2 + rtt3) / 3, 2)

                hops.append({
                    'hop_number': hop_num,
                    'ip_address': ip,
                    'hostname'  : '',
                    'rtt1_ms'   : rtt1,
                    'rtt2_ms'   : rtt2,
                    'rtt3_ms'   : rtt3,
                    'avg_rtt_ms': avg,
                    'is_timeout': False,
                })
                continue
        else:
            # Linux format: " 1  192.168.1.1  1.234 ms  1.456 ms  1.789 ms"
            normal_match = re.match(
                r'^\s*(\d+)\s+(\S+)\s+([\d.]+)\s+ms\s+([\d.]+)\s+ms\s+([\d.]+)\s+ms',
                line
            )
            if normal_match:
                hop_num = int(normal_match.group(1))
                ip      = normal_match.group(2)
                rtt1    = float(normal_match.group(3))
                rtt2    = float(normal_match.group(4))
                rtt3    = float(normal_match.group(5))
                avg     = round((rtt1 + rtt2 + rtt3) / 3, 2)

                hops.append({
                    'hop_number': hop_num,
                    'ip_address': ip,
                    'hostname'  : '',
                    'rtt1_ms'   : rtt1,
                    'rtt2_ms'   : rtt2,
                    'rtt3_ms'   : rtt3,
                    'avg_rtt_ms': avg,
                    'is_timeout': False,
                })
                continue

        # Fallback: Extract any IP with timing
        partial_match = re.match(
            r'^\s*(\d+)\s+.*?([\d]{1,3}\.[\d]{1,3}\.[\d]{1,3}\.[\d]{1,3}).*?([\d.]+)\s+ms',
            line
        )
        if partial_match:
            hop_num = int(partial_match.group(1))
            ip      = partial_match.group(2)
            rtt     = float(partial_match.group(3))
            hops.append({
                'hop_number': hop_num,
                'ip_address': ip,
                'hostname'  : '',
                'rtt1_ms'   : rtt,
                'rtt2_ms'   : 0,
                'rtt3_ms'   : 0,
                'avg_rtt_ms': rtt,
                'is_timeout': False,
            })

    return hops

# ──────────────────────────────────────────────────
# SWITCH KO TRACE KARO + SAVE KARO
# ──────────────────────────────────────────────────
def trace_switch(switch):
    from .models import TraceRoute, TraceHop

    print(f"[TRACE] {switch.name} ({switch.ip_address}) trace running")

    output = run_traceroute(switch.ip_address)

    if not output:
        TraceRoute.objects.create(
            target_ip   = switch.ip_address,
            target_name = switch.name,
            status      = 'failed',
            total_hops  = 0,
        )
        print(f"[TRACE] {switch.name} → Failed!")
        return

    hops = parse_traceroute(output)

    if not hops:
        TraceRoute.objects.create(
            target_ip   = switch.ip_address,
            target_name = switch.name,
            status      = 'failed',
            total_hops  = 0,
        )
        return

    # Total RTT — last valid hop
    valid_hops  = [h for h in hops if not h['is_timeout']]
    total_rtt   = valid_hops[-1]['avg_rtt_ms'] if valid_hops else 0

    trace = TraceRoute.objects.create(
        target_ip    = switch.ip_address,
        target_name  = switch.name,
        status       = 'success',
        total_hops   = len(hops),
        total_rtt_ms = total_rtt,
    )

    # Har hop save karo
    for hop in hops:
        TraceHop.objects.create(
            traceroute  = trace,
            hop_number  = hop['hop_number'],
            ip_address  = hop['ip_address'],
            hostname    = hop['hostname'],
            rtt1_ms     = hop['rtt1_ms'],
            rtt2_ms     = hop['rtt2_ms'],
            rtt3_ms     = hop['rtt3_ms'],
            avg_rtt_ms  = hop['avg_rtt_ms'],
            is_timeout  = hop['is_timeout'],
        )

    print(f"[TRACE] {switch.name} → {len(hops)} hops | {total_rtt}ms ")

# ──────────────────────────────────────────────────
# SABHI SWITCHES KO TRACE KARO
# ──────────────────────────────────────────────────
def trace_all_switches():
    from .models import ManagedSwitch
    for sw in ManagedSwitch.objects.filter(is_active=True):
        try:
            trace_switch(sw)
        except Exception as e:
            print(f"[TRACE ERR] {sw.name}: {e}")

# ──────────────────────────────────────────────────
# BACKGROUND THREAD
# ──────────────────────────────────────────────────
def _trace_loop():
    time.sleep(10)  
    print("[OK] Traceroute Monitor Started")
    while True:
        try:
            trace_all_switches()
        except Exception as e:
            print(f"[TRACE LOOP ERR] {e}")
        time.sleep(TRACE_INTERVAL)

def run_trace_monitor():
    t = threading.Thread(target=_trace_loop, daemon=True)
    t.start()
