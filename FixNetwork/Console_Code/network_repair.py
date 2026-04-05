# Developer ::> Gehan Fernando
import ctypes, subprocess, sys, time
from colorama import init, Fore, Style
from tqdm import tqdm

# Initialize colorama
try:
    init()
except Exception:
    class _X:
        RED = GREEN = YELLOW = CYAN = ""
        RESET_ALL = ""
    Fore = Style = _X()

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False

def run(cmd: str, use_tqdm: bool = False) -> bool:
    p = subprocess.run(cmd, shell=True, text=True, capture_output=True)
    ok = (p.returncode == 0)

    msg = (Fore.GREEN + "✔ " if ok else Fore.RED + "✖ ") + cmd + Style.RESET_ALL

    if use_tqdm:
        tqdm.write(msg)
        if not ok:
            if p.stdout.strip():
                tqdm.write(p.stdout.strip())
            if p.stderr.strip():
                tqdm.write(p.stderr.strip())
    else:
        print(msg)
        if not ok:
            if p.stdout.strip():
                print(p.stdout.strip())
            if p.stderr.strip():
                print(p.stderr.strip())

    return ok

def main():
    if not is_admin():
        print(Fore.RED + "Run as Administrator." + Style.RESET_ALL)
        return

    steps = [
        # -------------------------
        # Diagnostics (before fix)
        # -------------------------
        ("Show IP configuration", "ipconfig /all"),
        ("Show routing table", "route print"),
        ("Show WinHTTP proxy", "netsh winhttp show proxy"),

        # -------------------------
        # DHCP + DNS cleanup
        # -------------------------
        ("Release DHCP lease", "ipconfig /release"),
        ("Flush DNS cache", "ipconfig /flushdns"),
        ("Register DNS", "ipconfig /registerdns"),
        ("Renew DHCP lease", "ipconfig /renew"),

        # -------------------------
        # Cache resets
        # -------------------------
        ("Clear ARP cache", "arp -d *"),
        ("Clear NetBIOS cache", "nbtstat -R"),
        ("Reload NetBIOS names", "nbtstat -RR"),

        # -------------------------
        # Proxy & SSL fixes
        # -------------------------
        ("Reset WinHTTP proxy", "netsh winhttp reset proxy"),
        ("Clear SSL state", "RunDll32.exe InetCpl.cpl,ClearMyTracksByProcess 8"),

        # -------------------------
        # Service restart (safe only)
        # -------------------------
        ("Restart WLAN service", 'powershell -Command "Restart-Service WlanSvc -Force"'),

        # -------------------------
        # Core network resets
        # -------------------------
        ("Reset TCP/IP stack", "netsh int ip reset"),
        ("Repair Winsock catalog", "netsh winsock reset"),

        # -------------------------
        # Optional deeper resets
        # -------------------------
        ("Reset IPv4 stack (optional)", "netsh int ipv4 reset"),
        ("Reset IPv6 stack (optional)", "netsh int ipv6 reset"),

        # -------------------------
        # Adapter restart (safe)
        # -------------------------
        ("Restart active adapters",
        'powershell -Command "Get-NetAdapter | Where-Object {$_.Status -eq \'Up\'} | Disable-NetAdapter -Confirm:$false; '
        'Start-Sleep -Seconds 2; '
        'Get-NetAdapter | Enable-NetAdapter -Confirm:$false"'),

        # -------------------------
        # Connectivity tests (after fix)
        # -------------------------
        ("Ping localhost", "ping -n 2 127.0.0.1"),
        ("Ping gateway",
        'powershell -Command "$gw=(Get-NetRoute -DestinationPrefix 0.0.0.0/0 | Select -First 1).NextHop; if($gw){ping -n 2 $gw}else{Write-Output \'No gateway found\'}"'),
        ("Ping public IP (Google DNS)", "ping -n 2 8.8.8.8"),
        ("Test DNS resolution", "nslookup google.com"),
    ]

    print(Fore.CYAN + "\nSafe Network Stabilization Routine\n" + Style.RESET_ALL)

    with tqdm(total=len(steps), unit="step") as pbar:
        for title, cmd in steps:
            pbar.set_description_str(title[:28])
            run(cmd, use_tqdm=True)
            time.sleep(0.3)
            pbar.update(1)

    print(Fore.CYAN + "\nFinished. Optional: reboot for maximum stability.\n" + Style.RESET_ALL)

if __name__ == "__main__":
    main()
