from pydbus import SystemBus
from gi.repository import GLib
import subprocess

# 블루투스 장치 초기화
subprocess.run(["sudo", "hciconfig", "hci0", "up"], check=True)
subprocess.run(["sudo", "sdptool", "add", "SP"], check=True)

# D-Bus 연결 설정
bus = SystemBus()

# 블루투스 어댑터 가져오기
adapter_path = "/org/bluez/hci0"
adapter = bus.get("org.bluez", adapter_path)

# 블루투스 어댑터를 Discoverable로 설정
adapter.SetDiscoveryFilter({"Transport": "auto"})
adapter.Powered = True
adapter.Discoverable = True
adapter.Pairable = True

# 블루투스 서버 설정
def on_device_connected(device):
    print(f"Device connected: {device}")

adapter.connect_to_signal("DeviceConnected", on_device_connected)

print("Waiting for connections...")

# 메인 루프 실행
GLib.MainLoop().run()
