# LAN Security Monitoring Dashboard

A Django-based LAN security monitoring system with a live web dashboard and lightweight Python client agents. It helps monitor connected machines, system health, USB activity, security alerts, banned IPs, and brute-force login attempts across a local network.

## Overview

LAN Security Monitoring Dashboard is designed for controlled LAN environments such as labs, classrooms, offices, and internal security testing setups.

The project contains two main parts:

- **Server Dashboard**: A Django-based monitoring server that receives data and displays it on a web dashboard.
- **Client Agent**: A Python-based endpoint agent that runs on client machines and sends system information to the server.

## Features

- Live LAN monitoring dashboard
- Python client agent for endpoint monitoring
- Online/offline machine tracking
- Hostname, IP address, MAC address, and OS information
- CPU, RAM, disk, and network usage monitoring
- USB connected/disconnected alerts
- Security alerts dashboard
- Brute-force detection middleware
- Automatic IP banning after failed login attempts
- Banned IP list with unban option
- Dark responsive dashboard UI
- REST-style API endpoints for agent communication

## Tech Stack

- Python
- Django
- SQLite
- HTML
- CSS
- JavaScript
- psutil
- requests
- PowerShell / WMI for Windows data collection
- Linux networking tools

## Project Structure

```text
LAN-Security-Monitoring-Dashboard/
├── README.md
├── manage.py
├── server_509/
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── monitor/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── middleware.py
│   ├── apps.py
│   └── templates/
│       └── monitor/
│           └── dashboard.html
└── AGENT/
    ├── README.md
    ├── agent.py
    └── install.bat
How It Works
The Django server runs on a central Linux/Kali machine.
The server listens on a static LAN IP address.
Client machines run the Python agent.
The agent collects endpoint system information.
The agent sends heartbeat and alert data to the Django API.
The dashboard displays machine status, resource usage, USB activity, alerts, and banned IPs in real time.
Server Setup
Clone the repository:
git clone https://github.com/Ares99913/LAN-Security-Monitoring-Dashboard.git
cd LAN-Security-Monitoring-Dashboard
Create and activate a virtual environment:
python3 -m venv venv
source venv/bin/activate
Install dependencies:
pip install django django-cors-headers psutil requests
Run migrations:
python manage.py makemigrations
python manage.py migrate
Start the Django server:
python manage.py runserver 0.0.0.0:8000
Dashboard URL:
http://SERVER_IP:8000/dashboard/
Example:
http://10.107.159.30:8000/dashboard/
Server Network Configuration
The monitoring server should use a static LAN IP so all agents can connect reliably.
Example server configuration:
IP Address: 10.107.159.30
Subnet Mask: 255.255.255.0
Gateway: 10.107.159.182
DNS: 8.8.8.8
Example NetworkManager commands:
sudo nmcli con mod ethernet-eth0 ipv4.addresses 10.107.159.30/24
sudo nmcli con mod ethernet-eth0 ipv4.gateway 10.107.159.182
sudo nmcli con mod ethernet-eth0 ipv4.dns "8.8.8.8 1.1.1.1"
sudo nmcli con mod ethernet-eth0 ipv4.method manual
sudo nmcli con down ethernet-eth0
sudo nmcli con up ethernet-eth0
Verify the IP:
ip -4 addr show eth0
Django Configuration
In settings.py, allow the server IP:
ALLOWED_HOSTS = ["10.107.159.30", "localhost", "127.0.0.1"]
Required apps:
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "monitor.apps.MonitorConfig",
]
Required middleware includes:
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    ...
    "monitor.middleware.BruteForceMiddleware",
]
Client Agent Setup
The client agent is located in:
AGENT/
Files:
AGENT/
├── agent.py
├── install.bat
└── README.md
Copy agent.py and install.bat to each Windows client machine.
Example:
C:\509-Agent\
├── agent.py
└── install.bat
In agent.py, configure the server IP:
SERVER_IP = "10.107.159.30"
SERVER_PORT = 8000
Run the agent:
install.bat
If connected successfully, the console will show:
[OK] CPU:... RAM:... USB:...
Client Static IP Example
If DHCP is not available, assign static IPs manually.
Example:
Server:   10.107.159.30
Laptop 1: 10.107.159.31
Laptop 2: 10.107.159.32
Laptop 3: 10.107.159.33
Subnet:   255.255.255.0
Gateway:  10.107.159.182
DNS:      8.8.8.8
Do not assign the server IP to any client machine.
API Endpoints
Endpoint	Method	Description
/dashboard/	GET	Web dashboard
/api/heartbeat/	POST	Receives agent heartbeat/system data
/api/alert/	POST	Receives USB/security alerts
/api/dashboard/	GET	Returns dashboard data
/api/banned-ips/	GET	Returns active banned IPs
/api/unban/<ip>/	POST	Unbans an IP address
/api/alerts/mark-read/	POST	Marks alerts as read
/api/login/	POST	Login endpoint used for brute-force detection

Agent Data Collected
The client agent collects and sends:
Hostname
IP address
MAC address
Operating system information
CPU usage
RAM usage
Total RAM
Disk usage
USB device list
USB device count
Network sent data
Network received data
USB Monitoring
The agent detects removable USB activity and sends alerts to the server.
Supported alert types:
USB_CONNECTED
USB_DISCONNECTED
These alerts appear in the dashboard under the Alerts section.
Brute-Force Detection
The project includes a Django middleware for brute-force detection.
If the same IP sends multiple failed login requests and receives 401 Unauthorized responses, the middleware bans the IP and creates a dashboard alert.
Default behavior:
3 failed attempts = IP banned
Alert type:
BRUTE_FORCE
Banned IPs can be viewed and unbanned from the dashboard.
Connectivity Testing
From a client machine:
ping 10.107.159.30
Open the dashboard:
http://10.107.159.30:8000/dashboard/
If the dashboard opens, the agent should also be able to connect.
Common Issues
Server is not reachable from client
Make sure the Django server is running on all interfaces:
python manage.py runserver 0.0.0.0:8000
Agent cannot find agent.py
Keep agent.py and install.bat in the same folder.
Correct:
C:\509-Agent\agent.py
C:\509-Agent\install.bat
Firewall blocks the dashboard
Allow port 8000 on the server:
sudo ufw allow 8000/tcp
Dashboard opens but buttons do not work
Hard refresh the browser:
Ctrl + F5
Also check the browser console for JavaScript errors.
GitHub push does not work from Kali
If Kali is on an isolated LAN without internet access, GitHub push will fail. Connect Kali to an internet-enabled network or push from a Windows machine with internet access.
Security Notice
This project is intended for educational, lab, and internal LAN monitoring use only. Do not expose the Django development server directly to the public internet.
For production use, configure:
HTTPS
Authentication
Secure secret management
Proper firewall rules
Production WSGI server
Environment variables for sensitive settings
Author
Created by Ares99913
License
This project is intended for educational and internal network monitoring purposes.
```
