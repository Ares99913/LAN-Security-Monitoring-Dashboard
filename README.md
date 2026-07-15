# 🔒 509 Server - Network Monitoring System

<div align="center">

**⚠️ PROPRIETARY SOFTWARE - ALL RIGHTS RESERVED ⚠️**

**Copyright © 2025 Ares99913**

![Python](https://img.shields.io/badge/Python-3.13-blue?style=for-the-badge&logo=python)
![Django](https://img.shields.io/badge/Django-5.2-green?style=for-the-badge&logo=django)
![License](https://img.shields.io/badge/License-Proprietary-red?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Production_Ready-success?style=for-the-badge)
![Copyright](https://img.shields.io/badge/Copyright-2025_Ares99913-orange?style=for-the-badge)

**A comprehensive real-time network monitoring solution for LAN environments**

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [API](#-api) • [Contributing](#-contributing)

</div>

---

## � Overview

509 Server is a powerful network monitoring system designed for enterprise LAN environments. It provides real-time monitoring of connected devices, SNMP-enabled switches, security alerts, and comprehensive network analytics through an intuitive web dashboard.

### 🎯 Key Capabilities

- **Real-time Agent Monitoring**: Track CPU, RAM, disk usage, and processes across all connected machines
- **SNMP Switch Management**: Monitor network switches, port status, and MAC address tables
- **Security Features**: Brute-force protection, ARP/DNS spoofing detection, and automated IP banning
- **USB Device Tracking**: Real-time alerts for USB connections and disconnections
- **Network Path Analysis**: Traceroute monitoring for network topology visualization
- **Responsive Dashboard**: Modern, auto-refreshing UI with live metrics and alerts

---

## ✨ Features

### 🖥️ Agent-Based Monitoring
- Real-time system metrics (CPU, RAM, Disk)
- Process monitoring and network statistics
- USB device detection with instant alerts
- Open ports scanning and tracking
- Cross-platform agent support (Windows primary)

### � SNMP Network Monitoring
- Switch discovery and management
- Port status and speed monitoring
- MAC address table tracking
- Link state change alerts
- Multi-switch support

### 🔐 Security & Compliance
- Brute-force attack prevention (auto-ban)
- ARP spoofing detection
- DNS spoofing detection
- Failed authentication tracking
- Comprehensive security event logging

### 📊 Analytics & Reporting
- Real-time dashboard with live updates
- Historical data tracking
- Alert management system
- Network topology visualization
- Export capabilities

---

## 🚀 Quick Start

### Prerequisites

- Python 3.13+
- Windows Server (primary support)
- Network connectivity (10.143.177.x subnet recommended)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/509-server.git
cd 509-server
```

2. **Create virtual environment**
```bash
python -m venv venv_win
venv_win\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Apply migrations**
```bash
python manage.py migrate
```

5. **Create admin user**
```bash
python manage.py createsuperuser
```

6. **Start the server**
```bash
python manage.py runserver 0.0.0.0:8080
```

7. **Access dashboard**
```
http://localhost:8080/
```

---

## 📦 Agent Deployment

### Building the Agent

```bash
# From project root
pyinstaller agent.spec
```

Agent executable will be available in `dist/agent.exe`

### Deploying to Client Machines

1. Copy `dist/agent.exe` to target machine
2. Run the executable (no installation required)
3. Agent will automatically connect to server

### Agent Configuration

Edit `agent.py` before building:

```python
SERVER_IP = "10.143.177.189"  # Your server IP
SERVER_PORT = 8080            # Server port
INTERVAL = 3                  # Heartbeat interval (seconds)
```

---

## � Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=False
ALLOWED_HOSTS=10.143.177.189,yourdomain.com
DATABASE_URL=sqlite:///db.sqlite3
```

### SNMP Switch Configuration

Add switches via Django admin or programmatically:

```python
from monitor.models import ManagedSwitch

ManagedSwitch.objects.create(
    name='Core Switch',
    ip_address='10.143.177.50',
    community='public',
    location='Server Room',
    total_ports=48,
    is_active=True
)
```

---

## 🌐 API Documentation

### Endpoints

#### Dashboard Data
```http
GET /api/dashboard/
```
Returns comprehensive system statistics and machine list.

**Response:**
```json
{
  "machines": [...],
  "alerts": [...],
  "total": 10,
  "online": 8,
  "offline": 2,
  "switches": [...]
}
```

#### Agent Heartbeat
```http
POST /api/heartbeat/
```
Receives agent telemetry data.

**Request Body:**
```json
{
  "hostname": "LAPTOP-001",
  "ip_address": "10.143.177.100",
  "cpu_percent": 45.2,
  "ram_percent": 62.1,
  ...
}
```

#### Switch Monitoring
```http
GET /api/switch/
```
Returns all configured switches with port details.

#### Traceroute
```http
GET /api/traceroute/
POST /api/traceroute/run/<ip>/
```
Retrieve or trigger network path traces.

#### Security Management
```http
GET /api/banned-ips/
POST /api/unban/<ip>/
POST /api/alerts/mark-read/
```

---

## 🏗️ Architecture

### System Components

```
┌─────────────────────────────────────────────────────────┐
│                    Web Dashboard                        │
│         (Real-time UI with auto-refresh)                │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                  Django Server                          │
│  ┌──────────────┬──────────────┬────────────────┐      │
│  │ API Layer    │ Monitoring   │ Security       │      │
│  │ (REST/JSON)  │ Services     │ Middleware     │      │
│  └──────────────┴──────────────┴────────────────┘      │
└────────┬───────────────┬──────────────┬─────────────────┘
         │               │              │
    ┌────▼───┐      ┌────▼────┐    ┌───▼────┐
    │ Agents │      │  SNMP   │    │ SQLite │
    │(Remote)│      │Switches │    │   DB   │
    └────────┘      └─────────┘    └────────┘
```

### Technology Stack

- **Backend**: Django 5.2
- **Database**: SQLite (PostgreSQL ready)
- **Frontend**: Vanilla JS with real-time updates
- **Monitoring**: PySNMP 5.1.0, psutil, scapy
- **Agent**: Python with PyInstaller compilation

---

## � Database Schema

### Core Models

- **Machine**: Connected agent devices
- **Alert**: System and security notifications
- **ManagedSwitch**: SNMP-enabled network switches
- **SwitchPort**: Individual switch port information
- **BannedIP**: Security ban list with auto-expiry
- **TraceRoute**: Network path analysis
- **TraceHop**: Individual trace route hops

---

## � Security Features

### Brute Force Protection

- Automatic IP banning after 4 failed attempts
- 5-minute detection window
- 15-minute ban duration
- Auto-unban functionality

### Network Security

- **ARP Spoofing Detection**: Monitors MAC address changes
- **DNS Spoofing Detection**: Tracks DNS resolution anomalies
- **Port Scanning Detection**: Identifies suspicious network scans

### Authentication

- Django's built-in authentication system
- Session-based security
- CSRF protection enabled
- Secure password hashing (PBKDF2)

---

## � Troubleshooting

### Common Issues

#### Port Already in Use
```bash
# Option 1: Use different port
python manage.py runserver 0.0.0.0:8080

# Option 2: Kill process
netstat -ano | findstr :8000
taskkill /F /PID <PID>
```

#### Agent Not Connecting
- Verify `SERVER_IP` matches your server
- Check firewall allows the specified port
- Ensure both server and agent are on same network
- Test connectivity: `ping <server-ip>`

#### SNMP Not Working
- Verify switch is network-reachable
- Confirm SNMP is enabled on switch
- Check community string is correct (default: "public")
- Ensure switch is on compatible subnet

---

## 🧪 Testing

### Run Tests
```bash
python manage.py test monitor
```

### Manual Testing

1. Start server in test mode
2. Run agent locally
3. Verify dashboard updates
4. Test USB alert (plug/unplug device)
5. Verify security features

---

## 📈 Performance

### Specifications

- **Concurrent Agents**: 100+ supported
- **Update Interval**: 3 seconds (configurable)
- **Dashboard Refresh**: 3 seconds
- **SNMP Polling**: 30 seconds
- **Database**: Optimized queries with indexes

### Scalability

- Horizontal scaling via load balancer
- PostgreSQL for production deployments
- Redis caching support
- Celery task queue ready

---

## 🛠️ Development

### Project Structure

```
509_Server/
├── manage.py              # Django CLI
├── agent.py               # Agent source code
├── agent.spec             # PyInstaller config
├── requirements.txt       # Python dependencies
├── .env.template          # Environment template
│
├── server_509/            # Django configuration
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── monitor/               # Main application
│   ├── models.py          # Database models
│   ├── views.py           # API endpoints
│   ├── urls.py            # URL routing
│   ├── middleware.py      # Security middleware
│   ├── snmp_monitor.py    # SNMP monitoring
│   ├── traceroute_monitor.py
│   ├── arp_monitor.py
│   ├── dns_monitor.py
│   └── templates/
│       └── monitor/
│           └── dashboard.html
│
└── dist/                  # Compiled binaries
    └── agent.exe
```

### Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

### Code Style

- Follow PEP 8 guidelines
- Use type hints where applicable
- Write descriptive commit messages
- Add tests for new features

---

## � Requirements

### Python Packages

```
Django>=5.2
pysnmp==5.1.0
psutil>=5.9.0
requests>=2.31.0
scapy>=2.5.0
django-cors-headers>=4.3.0
pyasn1>=0.4.8
PyInstaller>=6.0.0
```

### System Requirements

- **Server**: Windows Server 2016+, Linux (experimental)
- **RAM**: 2GB minimum, 4GB recommended
- **Storage**: 1GB for application, more for logs
- **Network**: LAN connectivity required

---

## 🗺️ Roadmap

### Version 2.1 (Planned)
- [ ] PostgreSQL migration guide
- [ ] Multi-tenant support
- [ ] Email alert notifications
- [ ] Export reports (PDF/CSV)
- [ ] Mobile-responsive dashboard improvements

### Version 2.2 (Future)
- [ ] Docker containerization
- [ ] Kubernetes deployment guide
- [ ] Machine learning anomaly detection
- [ ] Advanced network topology mapping
- [ ] RESTful API v2 with authentication

---

## 📄 License & Copyright

**Copyright © 2025 Ares99913. All Rights Reserved.**

This project is **proprietary software** and is protected by copyright law.

### ⚠️ Usage Restrictions

- ❌ **Commercial use** is PROHIBITED without written permission
- ❌ **Redistribution** is PROHIBITED without written permission
- ❌ **Selling or sublicensing** is PROHIBITED
- ❌ **Unauthorized copying** is illegal

### ✅ Permitted Use

- ✅ Personal educational purposes only
- ✅ Non-commercial research (with attribution)
- ✅ Reference and learning

### 📜 License Details

See the [LICENSE](LICENSE) file for complete terms and conditions.

**For commercial licensing inquiries**: Contact [@Ares99913](https://github.com/Ares99913)

---

## ⚖️ Legal Notice

This software is the intellectual property of Ares99913. Unauthorized use, reproduction, 
or distribution may result in severe civil and criminal penalties, and will be 
prosecuted to the maximum extent possible under the law.

**© 2025 Ares99913. All Rights Reserved. Unauthorized use is strictly prohibited.**

---

## 👥 Authors

- **Developer** - Initial work and maintenance

---

## 🙏 Acknowledgments

- Django framework team
- PySNMP contributors
- Open source community
- Beta testers and early adopters

---

## � Support

### Getting Help

- **Documentation**: [GitHub Wiki](https://github.com/yourusername/509-server/wiki)
- **Issues**: [GitHub Issues](https://github.com/yourusername/509-server/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/509-server/discussions)

### Reporting Bugs

Please use the issue tracker and include:
- System information (OS, Python version)
- Steps to reproduce
- Expected vs actual behavior
- Relevant logs or screenshots

---

## 📊 Statistics

<div align="center">

![GitHub stars](https://img.shields.io/github/stars/yourusername/509-server?style=social)
![GitHub forks](https://img.shields.io/github/forks/yourusername/509-server?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/yourusername/509-server?style=social)

</div>

---

## 🌟 Show Your Support

Give a ⭐️ if this project helped you!

---

<div align="center">

**Made with ❤️ for network administrators**

[⬆ Back to Top](#-509-server---network-monitoring-system)

</div>

