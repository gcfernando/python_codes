# Developer ::> Gehan Fernando

# This script retrieves and displays all saved Wi-Fi SSIDs and their corresponding passwords on a Windows machine.
import subprocess
import re

# Get all saved Wi-Fi profiles
profiles_output = subprocess.check_output(
    ["netsh", "wlan", "show", "profiles"],
    text=True,
    errors="ignore"
)

profiles = re.findall(r"All User Profile\s*:\s*(.+)", profiles_output)

# Loop through each profile and get password
for profile in profiles:
    profile = profile.strip()

    profile_output = subprocess.check_output(
        ["netsh", "wlan", "show", "profile", profile, "key=clear"],
        text=True,
        errors="ignore"
    )

    password_match = re.search(r"Key Content\s*:\s*(.+)", profile_output)
    password = password_match.group(1) if password_match else "No password"

    print(f"SSID: {profile}")
    print(f"Password: {password}")
    print("-" * 30)

# This script deletes all saved Wi-Fi profiles on a Windows machine, except for a specified SSID.
ignore_ssid = "WIFI_NAME"

# Get all saved Wi-Fi profiles
profiles_output = subprocess.check_output(
    ["netsh", "wlan", "show", "profiles"],
    text=True,
    errors="ignore"
)

profiles = re.findall(r"All User Profile\s*:\s*(.+)", profiles_output)

# Delete each profile
for profile in profiles:
    profile = profile.strip()

    if profile == ignore_ssid:
        print(f"Skipping profile: {profile}")
        continue

    subprocess.run(
        ["netsh", "wlan", "delete", "profile", f"name={profile}"],
        errors="ignore"
    )

    print(f"Deleted profile: {profile}")
