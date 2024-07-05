from pydbus import SystemBus
from gi.repository import GLib
import subprocess
import time

# 블루투스 장치 초기화
subprocess.run(["sudo", "hciconfig", "hci0", "up"], check=True)
subprocess.run(["sudo", "sdptool", "add", "SP"], check=True)

# D-Bus 연결 설정
bus = SystemBus()

# 블루투스 어댑터 가져오기
adapter_path = "/org/bluez/hci0"
adapter = bus.get("org.bluez", adapter_path)

# 블루투스 어댑터를 Discoverable로 설정
discovery_filter = {
    "Transport": GLib.Variant("s", "auto")
}
adapter.SetDiscoveryFilter(discovery_filter)
adapter.Powered = True
adapter.Discoverable = True
adapter.Pairable = True

# 장치 연결 상태 확인 함수
def check_device_connection():
    managed_objects = bus.get("org.bluez", "/").GetManagedObjects()
    for path, interfaces in managed_objects.items():
        if "org.bluez.Device1" in interfaces:
            device = interfaces["org.bluez.Device1"]
            if device["Connected"]:
                print(f"Device connected: {path}")
    return True

# 주기적으로 장치 연결 상태 확인 (1초마다)
GLib.timeout_add_seconds(1, check_device_connection)

print("Waiting for connections...")

# 메인 루프 실행
GLib.MainLoop().run()
