# Developer ::> Gehan Fernando
# import libraries
import pywifi

# Initialize Wi-Fi interface
wifi_interface = pywifi.PyWiFi().interfaces()[0]

try:
    # Scan for Wi-Fi networks
    wifi_interface.scan()
    networks = wifi_interface.scan_results()

    # Define security modes and authentication modes
    akm_modes = ['OPEN', 'WPA-PSK', 'WPA-EAP', 'WPA2-PSK', 'WPA2-EAP', 'UNKNOWN']
    auth_modes = ['OPEN', 'SHARED', 'LEAP', 'WPA', 'WPA_PSK', 'WPA2', 'WPA2_PSK', 'UNKNOWN']

    # Print information about each network
    for network in networks:
        print(f"SSID: {network.ssid}")
        print(f"BSSID: {network.bssid[:-1].upper()}")
        print(f"Signal Strength (dBm): {network.signal}")
        print(f"Frequency (MHz): {network.freq / 1000000}")

        mode_index = 0

        if network.akm:
            mode_index = network.akm[0]
            print(f"Security Mode: {akm_modes[mode_index]}")

        if network.auth:
            mode_index = network.auth[0]
            print(f"Security Auth: {auth_modes[mode_index]}")

        print("\n")

except Exception as e:
    print(f"Error occurred: {e}")