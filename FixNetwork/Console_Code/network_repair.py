# Developer ::> Gehan Fernando
import ctypes, subprocess, sys, time

try:
    from colorama import init, Fore, Style
    init()
except Exception:
    class _X:
        RED = GREEN = YELLOW = CYAN = ""
        RESET_ALL = ""
    Fore = Style = _X()

try:
    from tqdm import tqdm
except Exception:
    tqdm = None

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False

def run(cmd: str, use_tqdm: bool = False) -> bool:
    p = subprocess.run(cmd, shell=True, text=True, capture_output=True)
    ok = (p.returncode == 0)

    msg = (Fore.GREEN + "✔ " if ok else Fore.RED + "✖ ") + cmd + Style.RESET_ALL
    if use_tqdm and tqdm is not None:
        tqdm.write(msg)
        if not ok:
            if p.stdout.strip(): tqdm.write(p.stdout.strip())
            if p.stderr.strip(): tqdm.write(p.stderr.strip())
    else:
        print(msg)
        if not ok:
            if p.stdout.strip(): print(p.stdout.strip())
            if p.stderr.strip(): print(p.stderr.strip())

    return ok

def main():
    if not is_admin():
        print(Fore.RED + "Run as Administrator." + Style.RESET_ALL)
        return

    steps = [
        # ---- LIGHTWEIGHT CACHE FIXES FIRST ----
        ("Flush DNS cache", "ipconfig /flushdns"),
        ("Register DNS", "ipconfig /registerdns"),

        # ---- REFRESH NETWORK ADDRESSING ----
        ("Renew DHCP lease", "ipconfig /renew"),

        # ---- LOCAL NETWORK CACHE CLEANUP ----
        ("Clear ARP cache", "arp -d *"),
        ("Clear NetBIOS cache", "nbtstat -R"),
        ("Reload NetBIOS names", "nbtstat -RR"),

        # ---- DEEPER NETWORK STACK REPAIRS ----
        ("Reset IPv4 stack", "netsh int ipv4 reset"),
        ("Reset IPv6 stack", "netsh int ipv6 reset"),
        ("Reset TCP/IP stack", "netsh int ip reset"),

        # ---- FINAL WINSOCK REPAIR (last) ----
        ("Repair Winsock catalog", "netsh winsock reset"),
    ]

    print(Fore.CYAN + "\nSafe Network Stabilization Routine\n" + Style.RESET_ALL)

    if tqdm is not None:
        with tqdm(total=len(steps), unit="step") as pbar:
            for title, cmd in steps:
                pbar.set_description_str(title[:28])  # use *_str for cleaner behavior
                ok = run(cmd, use_tqdm=True)          # see run() below
                time.sleep(0.3)
                pbar.update(1)
    else:
        for title, cmd in steps:
            print(Fore.YELLOW + f"→ {title}" + Style.RESET_ALL)
            run(cmd)
            time.sleep(0.3)

    print(Fore.CYAN + "\nFinished. Optional: reboot for maximum stability.\n" + Style.RESET_ALL)

if __name__ == "__main__":
    main()
