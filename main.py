import json
import platform
import re
import socket
import subprocess
from datetime import datetime
from pathlib import Path


# --------------------------------------------------
# 1. PROJECT CONFIGURATION
# --------------------------------------------------

PROJECT_DIR = Path(__file__).resolve().parent
REPORTS_DIR = PROJECT_DIR / "reports"


# --------------------------------------------------
# 2. RUN WINDOWS COMMANDS
# --------------------------------------------------

def run_command(command):
    """Execute a command and capture its output."""
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            errors="replace",
            timeout=10,
        )
        return (result.stdout + "\n" + result.stderr).strip()

    except (subprocess.TimeoutExpired, OSError) as error:
        return f"Command could not complete: {error}"


# --------------------------------------------------
# 3. DETECT THE DEFAULT GATEWAY
# --------------------------------------------------

def get_default_gateway():
    """Find the IPv4 default gateway from the route table."""
    output = run_command(["route", "print", "-4"])

    pattern = (
        r"^\s*0\.0\.0\.0\s+0\.0\.0\.0\s+"
        r"(\d{1,3}(?:\.\d{1,3}){3})\s+"
    )

    for line in output.splitlines():
        match = re.search(pattern, line)

        if match:
            gateway = match.group(1)

            if gateway != "0.0.0.0":
                return gateway

    return None


# --------------------------------------------------
# 4. TEST CONNECTIVITY
# --------------------------------------------------

def ping_host(host):
    """Attempt one ping and capture the result."""
    output = run_command(
        ["ping", "-n", "1", "-w", "2000", host]
    )

    successful = (
        "TTL=" in output.upper()
        or "TTL " in output.upper()
    )

    return {
        "host": host,
        "reachable_by_ping": successful,
        "details": output
    }


# --------------------------------------------------
# 5. CHECK DNS RESOLUTION
# --------------------------------------------------

def check_dns(domain):
    """Check whether a domain name can be resolved."""
    try:
        addresses = sorted({
            item[4][0]
            for item in socket.getaddrinfo(domain, None)
        })

        return {
            "domain": domain,
            "resolved": True,
            "addresses": addresses
        }

    except socket.gaierror as error:
        return {
            "domain": domain,
            "resolved": False,
            "error": str(error)
        }


# --------------------------------------------------
# 6. GENERATE THE DIAGNOSTIC REPORT
# --------------------------------------------------

def save_report(report):
    """Save diagnostic results as text and JSON files."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    filename = datetime.now().strftime(
        "diagnostic_%Y%m%d_%H%M%S_%f"
    )

    json_path = REPORTS_DIR / f"{filename}.json"
    text_path = REPORTS_DIR / f"{filename}.txt"

    json_path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    text_path.write_text(
        "WINDOWS NETWORK DIAGNOSTIC REPORT\n"
        + "=" * 40
        + "\n\n"
        + json.dumps(report, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    return text_path, json_path


# --------------------------------------------------
# 7. MAIN PROGRAM
# --------------------------------------------------

def main():
    timestamp = datetime.now().astimezone().isoformat(
        timespec="seconds"
    )

    print("=" * 55)
    print("       WINDOWS NETWORK DIAGNOSTIC TOOL")
    print("=" * 55)

    print(f"\nTime: {timestamp}")
    print(f"Operating system: {platform.platform()}")

    # Check 1: Network configuration
    print("\n[1/4] Collecting network configuration...")

    network_config = run_command(["ipconfig"])

    if network_config:
        print(network_config)
    else:
        print("No network configuration output was returned.")

    # Check 2: Default gateway
    print("\n[2/4] Detecting the default gateway...")

    gateway = get_default_gateway()

    if gateway:
        print(f"Default gateway detected: {gateway}")
        gateway_test = ping_host(gateway)

        print(
            "Gateway ping:",
            "Response received"
            if gateway_test["reachable_by_ping"]
            else "No ping response"
        )
    else:
        print("Default gateway could not be detected.")
        gateway_test = None

    # Check 3: External IP connectivity
    print("\n[3/4] Testing external IP connectivity...")

    external_test = ping_host("1.1.1.1")

    print(
        "External ping:",
        "Response received"
        if external_test["reachable_by_ping"]
        else "No ping response"
    )

    # Check 4: DNS resolution
    print("\n[4/4] Checking DNS resolution...")

    dns_test = check_dns("example.com")

    print(
        "DNS resolution:",
        "Successful"
        if dns_test["resolved"]
        else "Failed"
    )

    if dns_test["resolved"]:
        print("Resolved addresses:", ", ".join(dns_test["addresses"]))

    # Collect results
    report = {
        "timestamp": timestamp,
        "operating_system": platform.platform(),
        "network_configuration": network_config,
        "default_gateway": gateway,
        "gateway_ping": gateway_test,
        "external_ping": external_test,
        "dns_check": dns_test,
        "limitations": [
            "A failed ping does not prove a network is down.",
            "DNS resolution alone does not prove all internet services work.",
            "Results require interpretation and may need further testing."
        ]
    }

    # Save results
    print("\nSaving diagnostic reports...")

    try:
        text_path, json_path = save_report(report)

        print(f"Text report: {text_path}")
        print(f"JSON report: {json_path}")

    except OSError as error:
        print(f"Could not save reports: {error}")

    print("\nDiagnostic process completed.")
    print("=" * 55)


# --------------------------------------------------
# 8. PROGRAM ENTRY POINT
# --------------------------------------------------

if __name__ == "__main__":
    main()