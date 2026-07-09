# 🛡️ 509 Server Agent v2

> **A Cross-Platform Endpoint Monitoring Agent for Enterprise Network Monitoring Systems**

The **509 Server Agent v2** is a lightweight endpoint monitoring agent developed in Python. It continuously collects real-time system information from client machines and securely sends it to a centralized monitoring server.

Designed for LAN environments, educational labs, small organizations, and cybersecurity projects, the agent provides continuous visibility into endpoint activity, hardware status, running processes, USB events, and network information.

---

# ✨ Features

## 💻 System Monitoring

* CPU Usage Monitoring
* RAM Usage Monitoring
* Disk Usage Monitoring
* Operating System Detection
* Hostname Detection
* IP Address Detection
* MAC Address Detection
* Device Type Detection
* System Boot Time
* Agent Uptime

---

## 🌐 Network Monitoring

* Active IP Discovery
* Network Traffic Statistics
* Open Port Detection
* Listening Services Detection
* Network Interface Information
* Real-Time Heartbeat Communication

---

## 🔌 USB Device Monitoring

* Detect USB Device Connection
* Detect USB Device Removal
* Automatic Alert Generation
* Device Information Collection

---

## ⚙ Process Monitoring

* Running Process Enumeration
* Process ID (PID)
* Process Status
* Username Information
* Process Count

---

## 🖥 Hardware Monitoring

* Connected Hardware Enumeration
* Storage Device Detection
* Plug and Play Device Detection
* Hardware Information Collection

---

## 🚨 Alert System

The agent automatically generates alerts for:

* USB Connected
* USB Removed
* Endpoint Status
* Heartbeat Failure
* Device Information Updates

---

# 📡 Communication

The agent communicates with the central monitoring server using REST APIs.

Heartbeat Endpoint

```
POST /api/heartbeat/
```

Alert Endpoint

```
POST /api/alert/
```

Data is transmitted in JSON format over HTTP.

---

# 🏗 Architecture

```
                    +-------------------------+
                    |   Central Server        |
                    | Django / Flask API      |
                    +-----------+-------------+
                                ^
                                |
                           HTTP REST API
                                |
      ----------------------------------------------------
      |                  LAN Network                      |
      ----------------------------------------------------
           |             |             |             |
      +---------+   +---------+   +---------+   +---------+
      | Agent   |   | Agent   |   | Agent   |   | Agent   |
      | PC #1   |   | PC #2   |   | PC #3   |   | PC #N   |
      +---------+   +---------+   +---------+   +---------+
```

---

# 🛠 Technologies Used

* Python 3
* psutil
* requests
* socket
* subprocess
* pathlib
* uuid
* platform
* JSON
* REST API

---

# 📦 Installation

Clone the repository

```bash
git clone https://github.com/your-username/509-server-agent.git
```

Move into the project

```bash
cd 509-server-agent
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run

```bash
python agent.py
```

---

# 🚀 Windows Startup Support

Install Startup

```bash
python agent.py --install-startup
```

Remove Startup

```bash
python agent.py --uninstall-startup
```

---

# 📊 Information Collected

* Hostname
* IP Address
* MAC Address
* Operating System
* Device Type
* CPU Usage
* RAM Usage
* Disk Usage
* Running Processes
* Open Ports
* Active Network IPs
* Hardware Devices
* USB Devices
* Network Statistics
* System Boot Time
* Agent Uptime

---

# 📂 Project Structure

```
509-server-agent/
│
├── agent.py
├── requirements.txt
├── README.md
└── LICENSE
```

---

# 🔒 Security Features

* Lightweight Endpoint Agent
* Automatic Heartbeat Reporting
* USB Event Detection
* Process Monitoring
* Hardware Inventory
* Network Visibility
* Real-Time Alert Generation

---

# 📈 Future Improvements

* Encrypted Communication (HTTPS)
* Screenshot Monitoring
* File Integrity Monitoring
* Remote Command Execution
* Event Log Collection
* Service Monitoring
* Firewall Status Detection
* Scheduled Tasks Monitoring
* Multi-Platform Support
* Dashboard Analytics

---

# 📜 License

This project is developed for **educational purposes**, cybersecurity research, and enterprise network monitoring demonstrations.

---

# 👨‍💻 Author

**Vansh Sharma**

Cyber Security Enthusiast • B.Tech CSE

⭐ If you found this project useful, consider giving it a star on GitHub.
