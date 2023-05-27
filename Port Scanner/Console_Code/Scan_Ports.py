# Developer Gehan Fernando
# import libraries
import socket
import multiprocessing
import psutil
import subprocess

def fetch_ip_address():
    hostname = socket.gethostname()
    return socket.gethostbyname(hostname)

def get_process_name(process_id):
    process = psutil.Process(process_id)
    return process.name()

def scan_ports(port, ip_address):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    try:
        result = sock.connect_ex((ip_address, port))

        if result == 0:
            message = f"Port {port} is open.\n"
            cmd = f"netstat -ano | findstr :{port}"
            output = subprocess.check_output(cmd, shell=True)
            process_id = output.strip().split()[-1].decode()
            process_name = get_process_name(int(process_id))
            message += f"Used by Process ID: {process_id}, Process Name: {process_name}\n"
            print(message)
        else:
            print(f"Port {port} is closed.\n")
    except Exception as e:
        print(f"Error occurred while scanning port {port}: {str(e)}\n")
    finally:
        sock.close()

if __name__ == "__main__":
    ip_address = fetch_ip_address()
    num_processes = multiprocessing.cpu_count()
    pool = multiprocessing.Pool(processes=num_processes)
    pool.starmap(scan_ports, [(port, ip_address) for port in range(1, 65536)])
    pool.close()
    pool.join()