# Developer ::> Gehan Fernando
# import libraries
import math
from speedtest import Speedtest

internet = Speedtest()

def test_speed():
    # Choose best server
    print("Loading servers")
    server = internet.get_best_server()

    # Calulating download speed
    print("Calulating download speed...")
    download_speed = internet.download()

    # Calulating upload speed
    print("Calulating upload speed...")
    upload_speed = internet.upload() 

    # Calulating ping result
    print("Calulating ping result...")
    ping_result = internet.results.ping

    # Display result
    print("\r\n")
    print(f"Choose best server {server['host']} located at {server['country']} Sponsor by {server['sponsor']}")
    print("Download \t:", bytes_to_mb(download_speed))
    print("Upload   \t:", bytes_to_mb(upload_speed))
    print("Ping     \t:", f"{ping_result:.2f} ms")

def bytes_to_mb(bytes):
    byteVal = int(math.floor(math.log(bytes, 1024)))
    power = math.pow(1024, byteVal)
    size = round(bytes / power, 2)
    return f"{size} Mbps"

if __name__ == "__main__":
   test_speed()