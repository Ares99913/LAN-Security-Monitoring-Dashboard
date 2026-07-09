import subprocess
import threading
import json
from django.utils import timezone
from datetime import timedelta
from .models import ManagedSwitch, SwitchPort, Alert

IF_DESCR         = ".1.3.6.1.2.1.2.2.1.2"
IF_OPER_STATUS   = ".1.3.6.1.2.1.2.2.1.8"
IF_SPEED         = ".1.3.6.1.2.1.2.2.1.5"
FDB_PORT         = ".1.3.6.1.2.1.17.4.3.1.2"
BASE_PORT_IFINDEX = ".1.3.6.1.2.1.17.1.4.1.2"

POLL_INTERVAL = 30  


def snmpwalk(ip, community, oid):
    try:
        r = subprocess.run(
            ["snmpwalk", "-v2c", "-c", community, "-On", ip, oid],
            capture_output=True, text=True, timeout=8
        )
        if r.returncode != 0:
            return []
        return [line.strip() for line in r.stdout.splitlines() if line.strip()]
    except Exception:
        return []

def parse_index_value(lines, base_oid):
    data = {}
    for line in lines:
        if " = " not in line:
            continue
        left, right = line.split(" = ", 1)
        index = left.replace(base_oid + ".", "").strip()
        value = right.split(": ", 1)[-1].strip()
        try:
            data[int(index)] = value
        except ValueError:
            pass
    return data

def mac_from_oid_suffix(suffix):
    try:
        parts = [int(x) for x in suffix.split(".")]
        return ":".join(f"{x:02x}" for x in parts)
    except Exception:
        return suffix


def poll_switch(sw):
    try:
        descr      = parse_index_value(snmpwalk(sw.ip_address, sw.community, IF_DESCR), IF_DESCR)
        status_raw = parse_index_value(snmpwalk(sw.ip_address, sw.community, IF_OPER_STATUS), IF_OPER_STATUS)
        speed_raw  = parse_index_value(snmpwalk(sw.ip_address, sw.community, IF_SPEED), IF_SPEED)
        bridge_map = parse_index_value(snmpwalk(sw.ip_address, sw.community, BASE_PORT_IFINDEX), BASE_PORT_IFINDEX)

        # MAC → if_index mapping
        mac_by_ifindex = {}
        for line in snmpwalk(sw.ip_address, sw.community, FDB_PORT):
            if " = " not in line:
                continue
            left, right = line.split(" = ", 1)
            mac_suffix  = left.replace(FDB_PORT + ".", "").strip()
            bridge_port = right.split(": ", 1)[-1].strip()
            try:
                if_index = bridge_map.get(int(bridge_port))
                if if_index:
                    mac_by_ifindex.setdefault(if_index, []).append(
                        mac_from_oid_suffix(mac_suffix)
                    )
            except ValueError:
                pass

        active_count = 0

        for if_index, name in descr.items():
            status_code = str(status_raw.get(if_index, "0"))
            if status_code == "1":
                status = "up"
                active_count += 1
            elif status_code == "2":
                status = "down"
            else:
                status = "unknown"

            try:
                speed_mbps = round(float(speed_raw.get(if_index, 0)) / 1_000_000, 2)
            except (ValueError, TypeError):
                speed_mbps = 0

            macs = mac_by_ifindex.get(if_index, [])

            # Port status change alert
            old = SwitchPort.objects.filter(switch=sw, if_index=if_index).first()
            if old and old.status != status:
                Alert.objects.create(
                    hostname      = sw.name,
                    ip_address    = sw.ip_address,
                    alert_type    = 'PORT_STATUS',
                    alert_message = f"{sw.name} Port {if_index} ({name}): {old.status.upper()} → {status.upper()}"
                )

            SwitchPort.objects.update_or_create(
                switch   = sw,
                if_index = if_index,
                defaults = {
                    'name'          : name,
                    'status'        : status,
                    'speed_mbps'    : speed_mbps,
                    'connected_macs': json.dumps(macs),
                    'mac_count'     : len(macs),
                }
            )

        # Switch summary update
        ManagedSwitch.objects.filter(pk=sw.pk).update(
            total_ports  = len(descr),
            active_ports = active_count,
            status       = 'online' if descr else 'offline',
            last_polled  = timezone.now(),
        )

        print(f"[SNMP] {sw.name} polled — {active_count}/{len(descr)} ports UP")

    except Exception as e:
        print(f"[SNMP ERR] {sw.name}: {e}")


# ── Poll All Switches ─────────────────────────────
def poll_all_switches():
    cutoff = timezone.now() - timedelta(seconds=POLL_INTERVAL)
    for sw in ManagedSwitch.objects.filter(is_active=True):
        if not sw.last_polled or sw.last_polled < cutoff:
            poll_switch(sw)


# ── Background Thread ─────────────────────────────
def _snmp_loop():
    import time
    import django
    django.setup()
    print("[OK] SNMP Monitor Started")
    while True:
        try:
            poll_all_switches()
        except Exception as e:
            print(f"[SNMP LOOP ERR] {e}")
        time.sleep(POLL_INTERVAL)


def run_snmp_monitor():
    t = threading.Thread(target=_snmp_loop, daemon=True)
    t.start()
