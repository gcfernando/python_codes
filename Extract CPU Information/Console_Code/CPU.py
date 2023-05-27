# Developer ::> Gehan Fernando
# import libraries
import psutil
import cpuinfo

# Get CPU information
info = cpuinfo.get_cpu_info()

cpu_version = info['cpuinfo_version_string']
brand = info['brand_raw']
architecture = info['arch']
hz_actual = info['hz_actual_friendly']

num_physical_cores = psutil.cpu_count(logical=False)
num_logical_cores = psutil.cpu_count(logical=True)

# current CPU frequency in MHz
freq = psutil.cpu_freq().current
# estimate temperature based on frequency
temperature = (freq / 100) + 15 

print(f"\r\nProcessor Info")
print(f"\tBrand            : {brand}")
print(f"\tArchitecture     : {architecture}")
print(f"\tVersion          : {cpu_version}")
print(f"\tActucal Hz       : {hz_actual}")
print(f"\tPhysical Cores   : {num_physical_cores}")
print(f"\tLogical Cores    : {num_logical_cores}")
print(f"\tTemperature      : {temperature}°C\r\n")