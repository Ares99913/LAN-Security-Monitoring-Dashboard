from scapy.all import sniff, ARP
from .models import BannedIP, Alert
import threading

known_arp_table = {}


def detect_arp_spoof(packet):
    if packet.haslayer(ARP):
        if packet[ARP].op == 2:
            ip  = packet[ARP].psrc
            mac = packet[ARP].hwsrc

            if ip in known_arp_table:
                old_mac = known_arp_table[ip]

                if old_mac != mac:
                    msg = (
                        f"ARP SPOOF DETECTED! "
                        f"IP: {ip} | "
                        f"Old MAC: {old_mac} | "
                        f"New MAC: {mac}"
                    )
                    print(f"[ALERT] {msg}")

                    Alert.objects.create(
                        hostname='Unknown',
                        ip_address=ip,
                        alert_type='ARP_SPOOF',
                        alert_message=msg
                    )

                    BannedIP.objects.get_or_create(
                        ip_address=ip,
                        defaults={'reason': 'ARP Spoofing'}
                    )
            else:
                known_arp_table[ip] = mac
                print(f"[ARP] Registered: {ip} → {mac}")


def start_arp_monitor():
    print("[OK] ARP Monitor...")
    sniff(
        filter="arp",
        prn=detect_arp_spoof,
        store=0
    )


def run_arp_monitor():
    thread = threading.Thread(
        target=start_arp_monitor,
        daemon=True
    )
    thread.start()
