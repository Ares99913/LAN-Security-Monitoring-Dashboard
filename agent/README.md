# Client Agent

The Client Agent is a lightweight Python script used by the LAN Security Monitoring Dashboard to collect endpoint system information and send it to the central Django server.

## Overview

The agent runs on client machines and periodically sends system health data to the monitoring server. It also detects USB device activity and sends alerts when removable devices are connected or disconnected.

## Files

| File | Description |
|---|---|
| `agent.py` | Collects system information and sends heartbeat data to the server |
| `install.bat` | Installs required Python packages and starts the agent on Windows |

## Requirements

- Windows 10/11
- Python 3.x
- Network connectivity to the monitoring server
- Required Python packages:
  - `psutil`
  - `requests`

## Configuration

Open `agent.py` and set the server IP address:

```python
SERVER_IP = "10.107.159.30"
SERVER_PORT = 8000
The server IP should point to the machine running the Django monitoring dashboard.
Usage
Keep both files in the same folder:
509-Agent\
├── agent.py
└── install.bat
Run the agent by double-clicking:
install.bat
If the connection is successful, the console will display live status updates:
[OK] CPU:... RAM:... USB:...
Data Collected
The agent collects and sends:
Hostname
IP address
MAC address
Operating system information
CPU usage
RAM usage
Total RAM
Disk usage
USB device count
USB device list
Network sent data
Network received data
API Communication
The agent sends heartbeat data to:
/api/heartbeat/
USB activity alerts are sent to:
/api/alert/
USB Monitoring
The agent monitors removable USB storage activity. When a USB device is connected or disconnected, the agent sends an alert to the server.
Supported alert types:
USB_CONNECTED
USB_DISCONNECTED
Troubleshooting
Server not found
Make sure the Django server is running:
python manage.py runserver 0.0.0.0:8000
Also verify that the server IP in agent.py is correct.
agent.py not found
Make sure agent.py and install.bat are in the same folder.
Dependencies not installed
Run:
python -m pip install psutil requests
Or run install.bat again.
Security Note
This agent is intended for educational, lab, and internal LAN monitoring environments. Review the code and network configuration before using it outside a controlled environment.