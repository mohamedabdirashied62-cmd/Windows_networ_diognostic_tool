Windows Network Diagnostic Tool

About the Project

A Python-based Windows network diagnostic tool designed to perform basic connectivity checks and generate diagnostic reports.

Features

- Collects network configuration using "ipconfig"
- Detects the default IPv4 gateway
- Tests gateway connectivity using ping
- Tests external IP connectivity
- Checks DNS resolution
- Generates timestamped TXT and JSON reports
- Handles command execution and DNS errors

Technologies

- Python 3
- Windows Command Line
- Networking Fundamentals
- JSON
- File Handling and Error Handling

How to Run

1. Install Python 3 on Windows.

2. Open a terminal in the project folder.

3. Run the command:
   
   python main.py

4. Review the generated reports in the "reports" folder.

Limitations

A failed ping does not necessarily mean that a network is unavailable. Firewalls may block ping requests, and successful DNS resolution does not guarantee that every internet service is working.

Purpose

This project demonstrates practical learning in Python programming, Windows troubleshooting, basic networking, and technical documentation.