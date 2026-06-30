from scapy.all import sniff, DNS
from .models import BannedIP, Alert
import threading

WHITELIST = [
    '8.8.8.8',      # Google DNS
    '8.8.4.4',      # Google DNS
    '1.1.1.1',      # Cloudflare
    '1.0.0.1',      # Cloudflare
    '9.9.9.9',      # Quad9
]

known_dns = {}

def detect_dns_spoof(packet):
    if packet.haslayer(DNS):
        dns = packet[DNS]
        if dns.qr == 1 and dns.ancount > 0:
            for i in range(dns.ancount):
                try:
                    answer = dns.an[i]
                    if answer.type == 1:
                        domain = answer.rrname.decode()
                        ip     = answer.rdata

                        #  WHITELIST CHECK — trusted IP 
                        if ip in WHITELIST:
                            known_dns[domain] = ip
                            return  # ignore this alert 

                        # domain record 
                        if domain in known_dns:
                            old_ip = known_dns[domain]
                            if old_ip != ip:
                                msg = (
                                    f"DNS SPOOF! "
                                    f"{domain} | "
                                    f"Real:{old_ip} "
                                    f"Fake:{ip}"
                                )
                                print(f"[ALERT] {msg}")

                                # Alert DB saved
                                Alert.objects.create(
                                    hostname='Network',
                                    ip_address=ip,
                                    alert_type='DNS_SPOOF',
                                    alert_message=msg
                                )

                                # Fake IP Banned list 
                                BannedIP.objects.get_or_create(
                                    ip_address=ip,
                                    defaults={
                                        'reason': 'DNS Spoofing'
                                    }
                                )
                        else:
                            # New domain register 
                            known_dns[domain] = ip
                            print(f"[DNS] Registered: {domain} → {ip}")

                except Exception as e:
                    pass  # ignore this error

def start_dns_monitor():
    print("[OK] DNS Monitor... (Whitelist Active)")
    sniff(
        filter="udp port 53",
        prn=detect_dns_spoof,
        store=0
    )

def run_dns_monitor():
    thread = threading.Thread(
        target=start_dns_monitor,
        daemon=True
    )
    thread.start()
